import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from aiohttp import web
import asyncio

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение."""
    await update.message.reply_text('Привет! Я эхо-бот.')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторяет сообщение пользователя."""
    await update.message.reply_text(update.message.text)

async def webhook_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выводит информацию о текущем вебхуке."""
    bot = context.bot
    info = await bot.get_webhook_info()
    await update.message.reply_text(f"Webhook Info:\n{info}")


async def webhook(request):
    """Обработчик вебхуков от Telegram."""
    bot = Bot(TELEGRAM_TOKEN)
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler('webhookinfo', webhook_info)) # Добавили!

    if request.method == 'POST':
        update = Update.de_json(await request.json(), bot)
        await application.process_update(update)
        return web.Response(text='OK')
    return web.Response(text='Bad Request', status=400)

async def vercel_handler(request):
    """Vercel handler."""
    app = web.Application()
    app.router.add_post('/api/telegram', webhook)  # Убедитесь, что путь совпадает с путем в vercel.json и в настройках вебхука Telegram!
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

    # Бесконечный цикл, чтобы функция не завершалась. Vercel сам управляет временем жизни функции.
    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    # Для локального тестирования (не для Vercel)
    import asyncio
    asyncio.run(vercel_handler(None))
