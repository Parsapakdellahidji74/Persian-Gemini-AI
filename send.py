#main.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from qa import generate_answer
from logger import logger

app = FastAPI(
    title="پرسش و پاسخ فارسی",
    description="یک API ساده برای پرسش و پاسخ با پشتیبانی از متن مرجع و حافظه مکالمه",
    version="1.0.0",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class QuestionRequest(BaseModel):
    chat_id: str
    question: str

@app.post("/ask", summary="پرسش سوال و دریافت پاسخ", tags=["پرسش و پاسخ"])
@limiter.limit("10/minute")
async def ask_question(request: Request, data: QuestionRequest):
    try:
        answer = await generate_answer(data.chat_id, data.question)
        logger.info(f"chat_id={data.chat_id} | question={data.question} | answer={answer}")
        return {"chat_id": data.chat_id, "question": data.question, "answer": answer}
    except Exception as e:
        logger.error(f"ERROR chat_id={data.chat_id} | {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در پردازش درخواست")
#chat_history
import json
from collections import defaultdict
from threading import Lock

memory_file = "chat_memory.json"
lock = Lock()

try:
    with open(memory_file, "r", encoding="utf-8") as f:
        chat_memory = defaultdict(list, json.load(f))
except FileNotFoundError:
    chat_memory = defaultdict(list)

def save_memory():
    with lock:
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(chat_memory, f, ensure_ascii=False, indent=2)

def append_to_history(chat_id: str, question: str, answer: str):
    chat_memory[chat_id].append({"question": question, "answer": answer})
    if len(chat_memory[chat_id]) > 5:
        chat_memory[chat_id] = chat_memory[chat_id][-5:]
    save_memory()

def get_history(chat_id: str, max_turns: int = 5):
    return chat_memory[chat_id][-max_turns:]
#db.py
import chromadb
from embedding import embed_fn

chroma_client = chromadb.Client()
DB_NAME = "googlecar_collection"

db = chroma_client.get_or_create_collection(
    name=DB_NAME,
    embedding_function=embed_fn,
)
#embdeing.py
import chromadb
from embedding import embed_fn

chroma_client = chromadb.Client()
DB_NAME = "googlecar_collection"

db = chroma_client.get_or_create_collection(
    name=DB_NAME,
    embedding_function=embed_fn,
)
#logger.py
import logging

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
#qa.py
from embedding import embed_fn, client
from db import db
from chat_history import append_to_history, get_history
from logger import logger

async def generate_answer(chat_id: str, question: str) -> str:
    try:
        embed_fn.document_mode = False
        result = db.query(query_texts=[question], n_results=3)
        retrieved_passages = result["documents"][0]

        prompt = (
            "تو یک دستیار فارسی‌زبان هستی که فقط با استفاده از متن‌های مرجع زیر به پرسش پاسخ می‌دهی.\n"
            "اگر پاسخ در متن‌ها وجود نداشت، بگو: «پاسخی بر اساس اطلاعات موجود ندارم.»\n\n"
        )

        history = get_history(chat_id)
        for turn in history:
            prompt += f"پرسش قبلی: {turn['question']}\nپاسخ قبلی: {turn['answer']}\n"

        prompt += f"پرسش: {question.strip()}\n"

        for passage in retrieved_passages:
            prompt += f"متن مرجع: {passage.strip()}\n"

        response = client.models.generate_content(
            model="gemini-2.0-pro",
            contents=prompt,
        )

        answer = response.text.strip()
        append_to_history(chat_id, question, answer)
        return answer
    except Exception as e:
        logger.error(f"Error in generate_answer: {str(e)}")
        return "متأسفانه در پاسخ به سوال شما مشکلی پیش آمد."


