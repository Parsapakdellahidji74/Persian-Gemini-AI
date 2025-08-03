// services
const fs = require('fs');
const path = require('path');
const pLimit = require('p-limit');

const memoryFile = path.join(__dirname, '..', 'memory.json');
let chatMemory = {};

if (fs.existsSync(memoryFile)) {
  chatMemory = JSON.parse(fs.readFileSync(memoryFile, 'utf-8'));
}

const limit = pLimit(1);

async function saveMemory() {
  await limit(() => {
    return fs.promises.writeFile(memoryFile, JSON.stringify(chatMemory, null, 2), 'utf-8');
  });
}

async function appendToHistory(chat_id, question, answer) {
  if (!chatMemory[chat_id]) {
    chatMemory[chat_id] = [];
  }

  chatMemory[chat_id].push({ question, answer });
  if (chatMemory[chat_id].length > 5) {
    chatMemory[chat_id] = chatMemory[chat_id].slice(-5);
  }

  await saveMemory();
}

function getHistory(chat_id, max_turns = 5) {
  return chatMemory[chat_id]?.slice(-max_turns) || [];
}

module.exports = { appendToHistory, getHistory };
