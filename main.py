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
