/**
 * @swagger
 * tags:
 *   name: Ask
 *   description: request & response 
 */

/**
 * @swagger
 * /ask:
 *   post:
 *     summary: Submitting a request and receiving a response
 *     tags: [Ask]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - chat_id
 *               - question
 *             properties:
 *               chat_id:
 *                 type: string
 *                 description: Chat Id
 *               question:
 *                 type: string
 *                 description: User Question
 *     responses:
 *       200:
 *         description: Succesfull Response
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 chat_id:
 *                   type: string
 *                 question:
 *                   type: string
 *                 answer:
 *                   type: string
 *       400:
 *         description: Validation Error
 *       500:
 *         description: Server Error
 */
// routes/ask.js
const express = require('express');
const router = express.Router();
const { generateAnswer } = require('../services/qa');
const logger = require('../utils/logger');

router.post('/', async (req, res, next) => {
  const { chat_id, question } = req.body;

  // Simple input Validation 
    if (typeof chat_id !== 'string' || typeof question !== 'string' || !chat_id.trim() || !question.trim()) {
    return res.status(400).json({ detail: 'he parameters chat_id and question must be non-empty strings.' });
  }

  try {
    const answer = await generateAnswer(chat_id, question);
    logger.info(`chat_id=${chat_id} | question=${question} | answer=${answer}`);
    res.json({ chat_id, question, answer });
  } catch (e) {
    logger.error(`ERROR chat_id=${chat_id} | ${e.message}`);
    next(e);
  }
});

module.exports = router;
