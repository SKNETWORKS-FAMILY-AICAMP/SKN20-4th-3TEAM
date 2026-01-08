from fastapi import FastAPI
from schemas import ChatRequest, ChatResponse
from prompt_module import run_rag

app = FastAPI(title = "3차 프로젝트 RAG Chatbot API")

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = run_rag(request.question)
    return {'answer': answer}

