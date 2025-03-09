from telegram import Update #///
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os  # Добавляем импорт модуля os


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

if __name__ == '__main__':
    # Загружаем токен из переменной окружения
    bot_token = os.environ.get("YOUR_BOT_TOKEN")

    if bot_token is None:
        print("Ошибка: Токен бота не найден в переменных окружения!")
        exit(1)  # Завершаем выполнение, если токена нет

    application = ApplicationBuilder().token(bot_token).build()  # Используем токен из переменной

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    print("Bot started. Webhook should be set up.")
