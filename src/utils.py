'''
유틸리티 함수 모음

문서 포맷팅: format_docs
리트리버 생성: get_retriever
Self-check 리트리버: self_check_retriver
RAG 시스템 초기화: initialize_rag_system
응답 기반 문서 필터링: filter_docs_by_response

'''
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from ensemble import EnsembleRetriever #커스텀 앙상블 리트리버 
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from prompt import self_check_prompt # 프롬포트 불러오기

import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
import pickle


# ---------------------------
# 문서 포맷팅 함수
# ---------------------------
def format_docs(docs):
    """문서를 출처 정보와 함께 포맷팅"""
    formatted_docs = []
    for doc in docs:
        metadata = doc.metadata
        
        # 데이터 유형에 따라 출처 정보 구성
        if metadata.get("source_type") == "qa_data":
            source_info = f"상담기록 - {metadata.get('lifeCycle', '')}/{metadata.get('department', '')}/{metadata.get('disease', '')}"
        else:
            source_info = f"서적 - {metadata.get('title', '')}"
            if metadata.get('author'):
                source_info += f" (저자: {metadata['author']})"
            if metadata.get('page'):
                source_info += f" p.{metadata['page']+1}"
        
        formatted_doc = f"""<document>
<content>{doc.page_content}</content>
<source_info>{source_info}</source_info>
<data_type>{metadata.get('source_type', 'unknown')}</data_type>
</document>"""
        
        formatted_docs.append(formatted_doc)
    
    return "\n\n".join(formatted_docs)

# print("문서 포맷팅 함수 생성 완.")


# ---------------------------
# Retriever 생성
# ---------------------------
def get_retriever(vectorstore, k_D=5, k_B=5):
    """
    앙상블 리트리버 생성 함수

    이 함수는 Dense 리트리버와 BM25 리트리버가 검색한 결과를 weights=[0.5, 0.5]로 합치는 앙상블 리트리버를 반환합니다.
    
    Args:
        vectorstore: 벡터스토어 객체

        k_D: Dense 리트리버가 검색할 문서 수
        k_B: BM25 리트리버가 검색할 문서 수
        """
    
    # 기본 리트리버
    retriever = vectorstore.as_retriever(search_kwargs={"k": k_D}, search_type="similarity")
    
    # BM25 리트리버를 생성하기 위해 벡터스토어에서 모든 문서 로드
    collection = vectorstore._collection
    doc_count = collection.count()
    
    if doc_count == 0:
        raise ValueError("벡터스토어가 비어있습니다.")
    
    all_data = collection.get(limit=doc_count)
    
    # Document 객체로 변환
    bm25_docs = []
    if all_data and 'ids' in all_data and len(all_data['ids']) > 0:
        documents = all_data.get('documents', [])
        metadatas = all_data.get('metadatas', [])
        
        for i, doc_id in enumerate(all_data['ids']):
            page_content = documents[i] if i < len(documents) else ""
            metadata = metadatas[i] if i < len(metadatas) else {}
            bm25_docs.append(Document(page_content=page_content, metadata=metadata))
    
    if len(bm25_docs) == 0:
        raise ValueError("벡터스토어에서 문서를 가져올 수 없습니다.")
    # print(f"BM25 리트리버용 문서 {len(bm25_docs)}개 로드 완료")

    # BM25 리트리버 생성
    retriever_bm25 = BM25Retriever.from_documents(bm25_docs)
    retriever_bm25.k = k_B # 검색 문서 개수
    

    # 앙상블 리트리버
    retriever_ensemble = EnsembleRetriever(
        retrievers=[retriever, retriever_bm25],
        weights=[0.5, 0.5]
    )
    
    return retriever_ensemble


# print("앙상블 리트리버 생성 함수 생성 완.")


# ---------------------------
# 검색 문서 필터링 함수 (LLM이 각 문서를 보고 KEEP/DROP 판단)
# ---------------------------
def self_check_retriver(found_docs, question, llm):
    '''
    이 함수는 사용자의 질문을 받아 검색된 문서들을 LLM이 검토하게 합니다. 
    LLM은 각 문서가 질문에 도움이 되는지 판단해 KEEP/DROP을 결정합니다. 
    결과적으로 KEEP인 문서만 반환합니다.
    '''

    # 환경변수 로드
    load_dotenv()
    if not os.environ.get('OPENAI_API_KEY'):
        raise ValueError('OPENAI_API_KEY 없음. .env 확인하세요')
    # print("OPENAI_API_KEY found.")

    #0. mini chain : 문서 keep or drop ?
    mini_chain = self_check_prompt() | llm | StrOutputParser()

    # 2. 문서별로 KEEP/DROP 판단
    kept_docs = []

    for doc in found_docs:
        decision = mini_chain.invoke({'question': question, 'doc': doc.page_content})
        print(f'\n문서 내용: {doc.page_content}\n판단: {decision}')

        if decision.strip().lower() == 'keep':
            kept_docs.append(doc)

    if len(kept_docs) == 0:
        print('모든 문서가 Drop되었습니다. 원래 검색된 문서들을 반환합니다.')
        kept_docs = found_docs  # 모든 문서가 Drop되면 원래 검색된 문서 반환

    print(f'\n최종 선택된 문서 개수: {len(kept_docs)}')

    return kept_docs

# print("검색 문서 필터링 함수 생성 완.")


# ---------------------------
# 초기화 함수: 벡터스토어 및 LLM 로드
# ---------------------------
def initialize_rag_system(vectorstore_path=r".\data\ChromaDB_bge_m3", collection_name="pet_health_qa_system_bge_m3"):
    """RAG 시스템 초기화 (벡터스토어, LLM, Retriever)"""
    
    # 임베딩 모델 로드
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 벡터스토어 로드
    vectorstore = Chroma(
        persist_directory=vectorstore_path,
        collection_name=collection_name,
        embedding_function=embeddings
    )
    print("벡터스토어가 성공적으로 로드되었습니다!")
        
    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # 앙상블 Retriever 생성 (앙상블)
    retriever = get_retriever(vectorstore, k=5)
    
    return {
        'vectorstore': vectorstore,
        'llm': llm,
        'retriever': retriever,
        'embeddings': embeddings
    }

# print("RAG 시스템 초기화 함수 생성 완.")


# ---------------------------
# filter_docs_by_response 함수: LLM 응답에서 실제로 사용된 문서만 필터링하여 반환
# ---------------------------
def filter_docs_by_response(docs, ai_response):
    """LLM 응답에서 실제로 사용된 문서만 필터링"""
    if not docs:
        return []
    
    used_docs = []
    
    for doc in docs:
        metadata = doc.metadata
        
        # 문서 출처 정보 생성
        if metadata.get("source_type") == "qa_data":
            lifecycle = metadata.get('lifeCycle', '').strip()
            department = metadata.get('department', '').strip()
            disease = metadata.get('disease', '').strip()
            
            if lifecycle and lifecycle in ai_response:
                used_docs.append(doc)
            elif department and department in ai_response:
                used_docs.append(doc)
            elif disease and disease in ai_response:
                used_docs.append(doc)
        else:
            title = metadata.get('title', '').strip()
            author = metadata.get('author', '').strip()
            
            if title and title in ai_response:
                used_docs.append(doc)
            elif author and author in ai_response:
                used_docs.append(doc)
        
        # 문서 내용 확인
        content = doc.page_content[:100].strip()
        if content and content in ai_response:
            if doc not in used_docs:
                used_docs.append(doc)
    
    if not used_docs and docs:
        used_docs.append(docs[0])
    
    return used_docs

# print("filter_docs_by_response 함수 생성 완.")

