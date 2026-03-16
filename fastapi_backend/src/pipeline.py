import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

from typing import TypedDict, List

# LangChain 임포트
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# LangGraph 임포트
from langgraph.graph import StateGraph, END

from .ensemble import EnsembleRetriever
from .prompt import get_rewrite_prompt, get_rag_prompt, get_rag_prompt2, self_check_prompt, get_intent_prompt
from .utils import format_docs, get_retriever, filter_docs_by_response

load_dotenv()

if not os.environ.get('OPENAI_API_KEY'):
    raise ValueError('OPENAI_API_KEY 없음. .env 확인하세요')

# LangSmith 설정 (환경변수가 있을 때만 활성화)
if os.environ.get('LANGSMITH_API_KEY'):
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGSMITH_PROJECT"] = "pet_rag"
    print("LangSmith 연결 완료")

# bge_m3 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# 환경 변수에서 벡터스토어 경로 읽기
chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "../data/ChromaDB_bge_m3")
print(f"벡터스토어 경로: {chroma_persist_dir}")

vectorstore = Chroma(
    persist_directory=chroma_persist_dir,
    collection_name="pet_health_qa_system_bge_m3",
    embedding_function=embeddings
)
print(f"벡터스토어 내 문서 개수: {vectorstore._collection.count()}")
print("벡터스토어가 성공적으로 로드되었습니다!")

# 앙상블 리트리버 생성 (Similarity + BM25, 0.5:0.5)
retriever = get_retriever(vectorstore, k_D=5, k_B=5)

# LLM 정의
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Rewrite 최대 반복 횟수
MAX_REWRITE = 2


# ─────────────────────────────────────────────────────────────
# LangGraph State 정의
# ─────────────────────────────────────────────────────────────

class RAGState(TypedDict):
    question: str
    dog_info: str
    intent: str              # "dog_health" | "other"
    rewritten_question: str
    docs: List[Document]
    context: str
    answer: str
    rewrite_count: int
    use_web_search: bool


# ─────────────────────────────────────────────────────────────
# 노드 함수 정의
# ─────────────────────────────────────────────────────────────

def classify_intent(state: RAGState) -> RAGState:
    """
    [노드 1] 의도 분류
    반려견 건강/의료 관련 질문인지 판단하여 검색 전략을 분기한다.
    """
    question = state["question"]

    intent_chain = get_intent_prompt() | llm | StrOutputParser()
    result = intent_chain.invoke({"question": question}).strip().lower()

    intent = "dog_health" if "dog_health" in result else "other"
    print(f"[의도 분류] '{question[:30]}...' → {intent}")

    return {**state, "intent": intent, "rewrite_count": 0}


def rewrite_query(state: RAGState) -> RAGState:
    """
    [노드 2] Query Rewriting
    자연어 질문을 검색 최적화 키워드 문장으로 변환한다.
    강아지 종류·나이·크기 맥락 보존, 접속사·감탄사 제거.
    """
    question = state["question"]
    rewrite_count = state.get("rewrite_count", 0)

    rewrite_chain = get_rewrite_prompt() | llm | StrOutputParser()
    rewritten = rewrite_chain.invoke({"question": question})

    print(f"[Query Rewrite #{rewrite_count + 1}] {question[:30]} → {rewritten[:40]}")

    return {**state, "rewritten_question": rewritten, "rewrite_count": rewrite_count + 1}


def retrieve_docs(state: RAGState) -> RAGState:
    """
    [노드 3] 앙상블 검색
    Similarity(벡터) + BM25 — 0.5:0.5 가중치로 문서를 검색한다.
    """
    query = state.get("rewritten_question") or state["question"]
    docs = retriever.invoke(query)
    print(f"[앙상블 검색] '{query[:30]}' → {len(docs)}개 문서 검색됨")

    return {**state, "docs": docs}


def evaluate_docs(state: RAGState) -> RAGState:
    """
    [노드 4] 관련성 평가 노드 (Threshold 기반)
    LLM이 각 문서를 KEEP/DROP 판단.
    관련 문서가 0개면 use_web_search=True로 설정 → Rewrite 루프 또는 웹검색 폴백으로 분기.
    """
    docs = state["docs"]
    question = state["question"]

    mini_chain = self_check_prompt() | llm | StrOutputParser()
    kept_docs = []

    for doc in docs:
        decision = mini_chain.invoke({"question": question, "doc": doc.page_content})
        if decision.strip().lower() == "keep":
            kept_docs.append(doc)

    actually_kept = len(kept_docs)
    print(f"[관련성 평가] KEEP: {actually_kept}/{len(docs)}개")

    if actually_kept == 0:
        # 관련 문서 없음 → Rewrite 루프 또는 웹검색으로 분기
        return {**state, "docs": [], "context": "", "use_web_search": True}
    else:
        context = format_docs(kept_docs)
        return {**state, "docs": kept_docs, "context": context, "use_web_search": False}


def web_search_fallback(state: RAGState) -> RAGState:
    """
    [노드 5] 웹 검색 폴백
    내부 DB로 관련 문서를 찾지 못했을 때 실시간 웹 검색으로 컨텍스트를 보완한다.
    """
    query = state.get("rewritten_question") or state["question"]

    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search_tool = DuckDuckGoSearchRun()
        search_result = search_tool.run(f"강아지 {query}")
        print(f"[웹 검색 폴백] '{query[:30]}' → {len(search_result)}자 결과 획득")

        context = (
            "<document>\n"
            f"<content>{search_result}</content>\n"
            "<source_info>웹 검색 결과 (DuckDuckGo)</source_info>\n"
            "<data_type>web_search</data_type>\n"
            "</document>"
        )
    except Exception as e:
        print(f"[웹 검색 오류] {e} — 빈 컨텍스트로 답변 생성")
        context = ""

    return {**state, "context": context, "use_web_search": False}


def generate_answer(state: RAGState) -> RAGState:
    """
    [노드 6] LLM 답변 생성
    할루시네이션 방지 프롬프트를 적용하여 최종 답변을 생성한다.
    강아지 프로필 유무에 따라 프롬프트를 분기한다.
    """
    dog_info = state.get("dog_info", "")
    context = state.get("context", "")
    question = state["question"]

    if dog_info:
        chain = get_rag_prompt() | llm | StrOutputParser()
        answer = chain.invoke({"question": question, "context": context, "dog_info": dog_info})
    else:
        chain = get_rag_prompt2() | llm | StrOutputParser()
        answer = chain.invoke({"question": question, "context": context})

    return {**state, "answer": answer}


# ─────────────────────────────────────────────────────────────
# 조건부 엣지 함수 정의
# ─────────────────────────────────────────────────────────────

def route_by_intent(state: RAGState) -> str:
    """의도에 따라 분기: 반려견 건강 관련 → 검색, 그 외 → 바로 답변"""
    if state["intent"] == "dog_health":
        return "rewrite"
    return "generate"


def route_after_evaluate(state: RAGState) -> str:
    """
    관련성 평가 결과에 따라 분기:
    - 관련 문서 있음 → 답변 생성
    - 없음 + rewrite 횟수 미달 → Rewrite 루프
    - 없음 + rewrite 횟수 초과 → 웹 검색 폴백
    """
    if not state.get("use_web_search", False):
        return "generate"

    if state.get("rewrite_count", 0) < MAX_REWRITE:
        print(f"[Rewrite 루프] 재검색 시도 ({state['rewrite_count']}/{MAX_REWRITE})")
        return "rewrite"

    print("[웹 검색 폴백] 최대 Rewrite 도달 → 웹 검색")
    return "web_search"


# ─────────────────────────────────────────────────────────────
# LangGraph 그래프 구성
# ─────────────────────────────────────────────────────────────

workflow = StateGraph(RAGState)

# 노드 등록
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("rewrite_query", rewrite_query)
workflow.add_node("retrieve_docs", retrieve_docs)
workflow.add_node("evaluate_docs", evaluate_docs)
workflow.add_node("web_search_fallback", web_search_fallback)
workflow.add_node("generate_answer", generate_answer)

# 시작 노드 설정
workflow.set_entry_point("classify_intent")

# 엣지 연결
workflow.add_conditional_edges(
    "classify_intent",
    route_by_intent,
    {
        "rewrite": "rewrite_query",
        "generate": "generate_answer",
    }
)
workflow.add_edge("rewrite_query", "retrieve_docs")
workflow.add_edge("retrieve_docs", "evaluate_docs")
workflow.add_conditional_edges(
    "evaluate_docs",
    route_after_evaluate,
    {
        "generate": "generate_answer",
        "rewrite": "rewrite_query",
        "web_search": "web_search_fallback",
    }
)
workflow.add_edge("web_search_fallback", "generate_answer")
workflow.add_edge("generate_answer", END)

# 그래프 컴파일
rag_graph = workflow.compile()
print("LangGraph RAG 파이프라인 컴파일 완료")


# ─────────────────────────────────────────────────────────────
# 외부 호출 인터페이스 (routers/chat.py 와 호환)
# ─────────────────────────────────────────────────────────────

def run_rag(question: str, dog_info: str = None) -> str:
    """
    LangGraph RAG 파이프라인 실행

    Args:
        question: 사용자 질문
        dog_info: 강아지 프로필 정보 (선택사항)

    Returns:
        AI 응답 문자열
    """
    initial_state: RAGState = {
        "question": question,
        "dog_info": dog_info or "",
        "intent": "",
        "rewritten_question": "",
        "docs": [],
        "context": "",
        "answer": "",
        "rewrite_count": 0,
        "use_web_search": False,
    }

    result = rag_graph.invoke(initial_state)
    return result["answer"]
