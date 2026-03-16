"""
quick_consistency_check.py
동일 질문을 여러 번 실행하여 RAG 답변의 일관성을 측정합니다.

사용법:
    python -m src.quick_consistency_check
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .pipeline import run_rag


def check_consistency(question: str, dog_info: str = None, n: int = 3) -> dict:
    """
    동일 질문을 n회 반복 실행하여 답변 일관성을 평가합니다.

    Args:
        question : 테스트할 질문
        dog_info : 강아지 프로필 정보 (선택사항)
        n        : 반복 횟수 (기본값: 3)

    Returns:
        {
            "question": str,
            "n_runs": int,
            "answers": List[str],
            "consistency_score": str,   # LLM 평가 점수 및 한 줄 요약
        }
    """
    answers = []
    for i in range(n):
        print(f"\n[실행 {i + 1}/{n}]")
        answer = run_rag(question, dog_info)
        answers.append(answer)
        print(f"답변 미리보기: {answer[:80]}...")

    # LLM 기반 일관성 평가
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    consistency_chain = (
        ChatPromptTemplate.from_template("""
다음은 동일한 질문에 대해 {n}회 생성된 RAG 챗봇 답변입니다.
핵심 의학 정보와 권고사항이 일관성 있게 유지되는지 평가하세요.

질문: {question}

{answers}

[평가 기준]
1. 동일한 핵심 원인/증상 언급 여부
2. 동일한 치료·관리 권고 여부
3. 모순되는 의학 정보 없는지

0~100점으로 일관성 점수를 매기고, 한 줄 평가를 작성하세요.
형식: "점수: XX점 | 평가: ..."
""")
        | llm
        | StrOutputParser()
    )

    answers_text = "\n\n".join(
        [f"--- 답변 {i + 1} ---\n{a}" for i, a in enumerate(answers)]
    )
    consistency_result = consistency_chain.invoke(
        {"n": n, "question": question, "answers": answers_text}
    )

    return {
        "question": question,
        "n_runs": n,
        "answers": answers,
        "consistency_score": consistency_result,
    }


if __name__ == "__main__":
    test_cases = [
        {
            "question": "강아지가 갑자기 피가 섞인 오줌을 싸요. 왜 이러는 걸까요?",
            "dog_info": None,
        },
        {
            "question": "강아지가 요즘 밥을 잘 안먹어요. 어떻게 해야 할까요?",
            "dog_info": None,
        },
        {
            "question": "강아지가 빙판에서 미끄러져서 걸을때 저는것 같아요.",
            "dog_info": "품종: 말티즈, 나이: 3살, 체중: 3kg, 중성화: 완료",
        },
    ]

    for tc in test_cases:
        print(f"\n{'=' * 60}")
        print(f"테스트 질문: {tc['question']}")
        result = check_consistency(tc["question"], dog_info=tc["dog_info"], n=3)
        print(f"\n[일관성 평가 결과]")
        print(result["consistency_score"])
        print(f"{'=' * 60}")
