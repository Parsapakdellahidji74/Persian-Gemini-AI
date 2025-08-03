// services/qa.js
const { getHistory, appendToHistory } = require('./chat_memory');
const db = require('./db');
const { client } = require('../utils/embedding');
const logger = require('../utils/logger');

function truncateText(text, maxLength = 500) {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

async function generateAnswer(chat_id, question) {
  try {
    const result = await db.query({
      query_texts: [question],
      n_results: 3,
    });

    const retrieved_passages = result.documents[0];

    let prompt = `تو یک دستیار فارسی‌زبان هستی که فقط با استفاده از متن‌های مرجع زیر به پرسش پاسخ می‌دهی.\n`;
    prompt += `اگر پاسخ در متن‌ها وجود نداشت، بگو: «پاسخی بر اساس اطلاعات موجود ندارم.»\n\n`;

    const history = getHistory(chat_id);
    history.forEach(turn => {
      prompt += `پرسش قبلی: ${turn.question}\nپاسخ قبلی: ${turn.answer}\n`;
    });

    prompt += `پرسش: ${question}\n`;
    retrieved_passages.forEach(p => {
      prompt += `متن مرجع: ${truncateText(p)}\n`;
    });

    const response = await client.models.generate_content({
      model: 'gemini-2.0-pro',
      contents: prompt,
    });

    const answer = response.text.trim();
    await appendToHistory(chat_id, question, answer);
    return answer;
  } catch (err) {
    logger.error(`Error in generateAnswer: ${err.message}`);
    return 'متأسفانه در پاسخ به سوال شما مشکلی پیش آمد.';
  }
}

module.exports = { generateAnswer };
