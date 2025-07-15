from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import json
import os

# Файл для хранения слов
VOCAB_FILE = "vocab.json"

# Функция загрузки словаря из файла
def load_vocab():
    if not os.path.exists(VOCAB_FILE):
        return []
    with open(VOCAB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Функция сохранения словаря в файл
def save_vocab(vocab):
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=4, ensure_ascii=False)

# Функция получения определения и примера слова
def get_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()[0]
        meaning = data["meanings"][0]["definitions"][0]
        definition = meaning["definition"]
        example = meaning.get("example", "No example available.")
        return {
            "word": word,
            "definition": definition,
            "example": example
        }
    else:
        return None

# Команда /add
async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❗ Используй так: /add <слово>")
        return

    word = context.args[0].lower()
    vocab = load_vocab()

    # Проверка, есть ли слово уже в словаре
    if any(entry["word"] == word for entry in vocab):
        await update.message.reply_text(f"⚠️ Слово \"{word}\" уже в словаре.")
        return

    # Получаем данные о слове
    word_data = get_word_data(word)
    if word_data:
        vocab.append(word_data)
        save_vocab(vocab)
        await update.message.reply_text(
            f"✅ Слово \"{word}\" добавлено!\n\n📖 Definition: {word_data['definition']}\n📌 Example: {word_data['example']}"
        )
    else:
        await update.message.reply_text(f"❌ Не удалось найти данные для слова \"{word}\".")

# Основной блок
async def main():
    app = ApplicationBuilder().token(os.environ["TELEGRAM_API_TOKEN"]).build()
    app.add_handler(CommandHandler("add", add_word))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

