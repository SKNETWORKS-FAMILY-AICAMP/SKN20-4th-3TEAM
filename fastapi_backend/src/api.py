from fastapi import FastAPI
from .schemas import ChatRequest, ChatResponse
from .pipeline import run_rag

app = FastAPI(title="강아지 질병 증상 RAG Chatbot API")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = run_rag(request.question)
    return {"answer": answer}
