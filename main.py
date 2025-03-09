import os
import random as rand
import time  # schedule убираем, он не нужен с вебхуками
from telegram import Update, WebhookInfo, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from aiohttp import web  # Добавляем aiohttp для создания веб-сервера

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SITE_URL = 'https://trychatgpt.ru'

# Настройка веб-драйвера
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')  # Добавляем disable-gpu
options.add_argument('--ignore-certificate-errors')

# ChromeDriver ВНУТРИ КОНТЕЙНЕРА Vercel, поэтому путь другой!
chrome_driver_path = '/usr/bin/chromedriver'  # ПУТЬ ВНУТРИ КОНТЕЙНЕРА!

# Инициализация веб-драйвера
service = Service(executable_path=chrome_driver_path)

# Инициализируем драйвер ГЛОБАЛЬНО, чтобы он был доступен во всех функциях.
# Это важно для serverless функций, чтобы не создавать драйвер каждый раз.
driver = webdriver.Chrome(service=service, options=options)


random_phrases = [
    "Андрей, держись бодрей! А то Петька отмерзнет!",
    "Ну что, заскучали? Так займитесь делом!",
    "Пора бы и за работу, но лучше выпейте по 100 грамм!",
    "Кто охотчий до еды, пусть пожалует сюды...",
    "Чем вы вообще вот занимаетесь, что я должен вас все время контролировать?",
    "Андрей! Прекрати ЭТО делать! Коллеги могут увидеть!",
    "Шайтаны, ну вы чего? Кто это опять такую кучу навалял?!",
    "Саня, расскажи про БАБ и про женщин!",
    "Вадик, проснись! Тебя все ищут!",
    "Перцы, рассказывайте кому что снилось сегодня?",
    "МЕРНЕМ ЖАНИД - значит на армянском (Дай мне умереть на твоем теле!)",
    "- Эх Яблочко да на тарелочке - Погибай же ты КОНТРА в перестрелочке!"
]

# Словарь для хранения ИСТОРИИ СООБЩЕНИЙ (глобальный)
chat_history = {}


async def send_message(bot: Bot, chat_id: int, text: str) -> None:
    await bot.send_message(chat_id=chat_id, text=text)

async def send_random_message(bot: Bot, chat_id: int) -> None:
    message = rand.choice(random_phrases)
    await send_message(bot, chat_id, message)

# start и random остаются почти без изменений, но используют bot из context
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправьте мне сообщение, и я перешлю его на trychatgpt.ru.')


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    await send_random_message(context.bot, chat_id)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    chat_id = update.message.chat_id

    if chat_id not in chat_history:
        chat_history[chat_id] = []
    chat_history[chat_id].append(user_message)
    if len(chat_history[chat_id]) > 20:
        chat_history[chat_id].pop(0)

    try:
        driver.get(SITE_URL)
        time.sleep(5)  #  Уменьшил время ожидания
        print("Сайт загружен")

        if "ChatGPT" not in driver.page_source:
          print("Страница не загружена")
          await update.message.reply_text("Извините, страница ChatGPT не загрузилась.")
          return # Выходим из функции, если страница не загрузилась

        input_field = driver.find_element(By.CSS_SELECTOR, 'textarea#input')
        print("Поле ввода найдено")
        input_field.send_keys(user_message)
        print(f"Сообщение '{user_message}' отправлено")
        input_field.send_keys(Keys.RETURN)
        time.sleep(5)  # Уменьшил время ожидания

        reply_elements = driver.find_elements(By.CSS_SELECTOR, 'div.message-content')
        if reply_elements:
            reply_text = reply_elements[-1].text
            print(f"Ответ найден: {reply_text}")
            if reply_text.strip().lower() != user_message.strip().lower():
                await update.message.reply_text(reply_text)
            else:
                await update.message.reply_text("Пожалуйста, подождите, я обрабатываю ваш запрос...")
                time.sleep(5) # Уменьшил время ожидания.
                reply_elements = driver.find_elements(By.CSS_SELECTOR, 'div.message-content')
                if reply_elements:
                    reply_text = reply_elements[-1].text
                    if reply_text.strip().lower() != user_message.strip().lower():
                        await update.message.reply_text(reply_text)
                    else:
                         await update.message.reply_text("Извините, я не могу обработать ваш запрос.")
                else:
                  await update.message.reply_text("Извините, я не могу обработать ваш запрос.")
        else:
          await update.message.reply_text("Извините, ответ не был найден.")


    except Exception as e:
        await update.message.reply_text(f'Произошла ошибка: {str(e)}')
        print(f'Ошибка: {str(e)}')



# ---  WEBHOOK  ---
async def webhook(request):
    """Обработчик вебхуков от Telegram."""
    bot = Bot(TELEGRAM_TOKEN)
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('random', random))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    if request.method == 'POST':
        update = Update.de_json(await request.json(), bot)
        await application.process_update(update)
        return web.Response(text='OK')
    return web.Response(text='Bad Request', status=400)


# ---  Vercel SERVERLESS FUNCTION ---
async def vercel_handler(request):
    """
    Эта функция будет вызываться Vercel при каждом запросе к вашему API endpoint.
    Она запускает aiohttp приложение, которое обрабатывает вебхуки.
    """

    app = web.Application()
    app.router.add_post('/api/telegram', webhook) #  /api/telegram - путь, который мы укажем в настройках Telegram
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))  # Слушаем на всех интерфейсах и порту из переменной окружения
    await site.start()

    # Бесконечный цикл, чтобы функция не завершалась.  Vercel сам управляет временем жизни функции.
    while True:
        await asyncio.sleep(3600)  # Ждем час (или другое большое значение)


# Точка входа для Vercel (и для локального запуска, если нужно)
if __name__ == '__main__':
  import asyncio
  asyncio.run(vercel_handler(None)) # Запуск для локального тестирования.  `None` - потому что request не нужен локально
