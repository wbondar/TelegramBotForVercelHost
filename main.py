from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv  # Нужно для локальной разработки, на Vercel не используется

load_dotenv() # Загружаем переменные из .env (только для локальной разработки)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

if __name__ == '__main__':
    # Загружаем токен из переменной окружения
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if bot_token is None:
        print("Ошибка: Токен бота не найден в переменных окружения!")
        exit(1)

    application = ApplicationBuilder().token(bot_token).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    print("Bot started. Webhook should be set up.") # Сообщение для отладки
    # !!!  application.run_polling() ЗДЕСЬ НЕ НУЖЕН  !!!
