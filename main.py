from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
app = web.Application()

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📲 Больше предложений в нашем канале", url="https://t.me/+ji-5MkKSIodkODE6"),
        InlineKeyboardButton("📝 Зарегистрироваться NUTS POKER", url="https://nutspoker.cc/club/AGENT"),
        InlineKeyboardButton("🌐 Перейти на наш сайт", url="https://poker-agent.org"),
    )
    await msg.answer(f"👋 Привет, {msg.from_user.first_name}!\n\nДобро пожаловать!\n\nВыбери интересующий тебя пункт:", reply_markup=kb)

async def on_startup(app):  # <- параметр 'app' нужен для aiohttp
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_URL')}/webhook"
    if not webhook_url or 'None' in webhook_url:
        raise ValueError("RENDER_EXTERNAL_URL не настроен корректно!")
    await bot.set_webhook(url=webhook_url)
    print(f"Webhook установлен: {webhook_url}")

async def handle_request(request):
    if request.method == "POST":
        update = types.Update(**await request.json())
        Dispatcher.set_current(dp)
        Bot.set_current(bot)
        await dp.process_update(update)
    return web.Response(text="OK")

app.router.add_post('/webhook', handle_request)
app.on_startup.append(on_startup)  # ✅ правильный способ для aiohttp

if name == '__main__':
    print(f"Запуск приложения на порту {os.getenv('PORT', 10000)}...")
    PORT = int(os.getenv("PORT", 10000))
    try:
        web.run_app(app, host='0.0.0.0', port=PORT)
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        raise