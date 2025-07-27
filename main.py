from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
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
    await msg.answer(f"👋 Привет!, {msg.from_user.first_name}!\n\nДобро пожаловать!\n\nВыбери интересующий тебя пункт:", reply_markup=kb)

async def on_startup(_):
    webhook_url = f"https://{os.getenv( ' RENDER_EXTERNAL_URL ')}/webhook"
    if not webhook_url or 'None' in webhook_url:
        raise ValueError("RENDER_EXTERNAL_URL не настроен корректно!")
    await bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}")
    

async def handle_request(request):
    return web.Response(text="Webhook is running")

app.router.add_get('/webhook', handle_request)
app.router.add_post('/webhook', dp.webhook())

if __name__ == ' __main__ ':
    PORT = int(os.getenv("PORT", 10000))
    web.run_app(app, host='0.0.0.0', port=PORT)