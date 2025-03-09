    import os
    from telegram import Update, Bot
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
    from dotenv import load_dotenv
    from aiohttp import web

    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text('Привет!')

    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(update.message.text)

    async def webhook(request):
        bot = Bot(TELEGRAM_TOKEN)
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        if request.method == 'POST':
            update = Update.de_json(await request.json(), bot)
            await application.process_update(update)
            return web.Response(text='OK')
        return web.Response(text='Bad Request', status=400)

    async def vercel_handler(request):
        app = web.Application()
        app.router.add_post('/api/telegram', webhook)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
        await site.start()
        while True:
            await asyncio.sleep(3600)

    if __name__ == '__main__':
      import asyncio
      asyncio.run(vercel_handler(None))
    
