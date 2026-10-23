"""FastAPI backend. Run: uvicorn api:app --reload"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from chatbot import HelpdeskBot

app = FastAPI(title="Student Helpdesk AI API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
bot = HelpdeskBot()

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=500)

@app.get("/health")
def health():
    return {"status": "ok", "intents": len(bot.topics)}

@app.post("/chat")
def chat(req: ChatRequest):
    return bot.answer(req.message)
