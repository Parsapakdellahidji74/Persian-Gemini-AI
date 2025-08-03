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
