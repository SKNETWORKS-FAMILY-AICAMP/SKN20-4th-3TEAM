import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

# LangChain 임포트
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma 
import chromadb
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from .ensemble import EnsembleRetriever
from .prompt import get_rewrite_prompt, get_rag_prompt,get_rag_prompt2, self_check_prompt # 프롬포트 불러오기
from .utils import format_docs, get_retriever, self_check_retriver, initialize_rag_system, filter_docs_by_response #유틸리티 함수 불러오기
load_dotenv()



if not os.environ.get('OPENAI_API_KEY'):
    raise ValueError('OPENAI_API_KEY 없음. .env 확인하세요')
# if not os.environ.get('LANGSMITH_API_KEY'):
#     raise ValueError('LANGSMITH_API_KEY 없음. env 확인하세요')

# os.environ["LANGSMITH_TRACING_V2"] = "true"
# os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGSMITH_PROJECT"] = "pet_rag"
# print("LangSmith 연결 완료")


'''
벡터 DB 불러오기
불러올때 생성시 임베딩 모델/컬렉션 이름과 동일해야 합니다!
'''


# bge_m3 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cpu'},  # GPU 사용시 'cuda'로 변경
    encode_kwargs={'normalize_embeddings': True}  # bge-m3는 정규화 권장
)

# 환경 변수에서 벡터스토어 경로 읽기
chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "../data/ChromaDB_bge_m3")
print(f"벡터스토어 경로: {chroma_persist_dir}")

vectorstore = Chroma( 
persist_directory=chroma_persist_dir,  # 환경 변수로 관리되는 경로
collection_name="pet_health_qa_system_bge_m3",
embedding_function=embeddings)

#벡터스토어 내 문서 개수 확인
print(f"벡터스토어 내 문서 개수: {vectorstore._collection.count()}")
print("벡터스토어가 성공적으로 로드되었습니다!")


# 앙상블 리트리버 생성
retriever = get_retriever(vectorstore, k_D=5, k_B=5)

# LLM 정의
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

   
def process_with_self_check(input_data):
    # input_data가 dict이면 question과 dog_info 추출, 아니면 question만
    if isinstance(input_data, dict):
        question_text = input_data.get('question', input_data.get('input', ''))
        dog_info = input_data.get('dog_info', '')
    else:
        question_text = input_data
        dog_info = ''

    # 1. 질문 재작성
    rewrite_chain = get_rewrite_prompt() | llm | StrOutputParser()
    rewritten_question = rewrite_chain.invoke({"question": question_text})
    
    # 2. 리트리버로 문서 검색
    found_docs = retriever.invoke(rewritten_question)
    
    # 3. self_check_retriver로 2차 필터링
    filtered_docs = self_check_retriver(found_docs, question_text, llm)
    
    # 4. 필터링된 문서로 context 생성
    context = format_docs(filtered_docs)
    
    return {
        "question": rewritten_question, #재작성한 질문
        "context": context, #2차 필터링된 문서로 만든 컨텍스트
        "dog_info": dog_info #강아지 프로필
    }

#RAG 파이프라인
rag_pipeline = RunnableLambda(process_with_self_check) | get_rag_prompt() | llm | StrOutputParser()
rag_pipeline2 = RunnableLambda(process_with_self_check) | get_rag_prompt2() | llm | StrOutputParser()


# fastapi에서 사용할 RAG 파이프라인 함수
def run_rag(question: str, dog_info: str = None) -> str:
    """
    RAG 파이프라인 실행
    
    Args:
        question: 사용자 질문
        dog_info: 강아지 프로필 정보 (선택사항)
    
    Returns:
        AI 응답 문자열
    """
    if dog_info:
        return rag_pipeline.invoke({"question": question, "dog_info": dog_info})
    else:
        # 강아지 정보가 없으면 빈 문자열로 처리
        return rag_pipeline2.invoke({"question": question, "dog_info": ""})

#테스트 코드 

'''
query = ["강아지가 갑자기 피가 섞인 오줌을 싸요. 왜 이러는 걸까요?",
          "강아지가 빙판에서 미끄러져서 걸을때 저는것 같아요. 집에서 해줄 수 있는 응급치료가 있을까요?",
          "강아지가 요즘 밥을 잘 안먹어요. 어떻게 해야 할까요?"]

for q in query:
    response = rag_pipeline.invoke(q)
    print("질문:", q)
    print("답변:", response)
'''
