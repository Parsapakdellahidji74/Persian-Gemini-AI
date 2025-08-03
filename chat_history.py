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
