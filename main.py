from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📲 Больше предложений в нашем канале", url="https://t.me/+ji-5MkKSIodkODE6"),
        InlineKeyboardButton("📝 Зарегистрироваться NUTS POKER", url="https://nutspoker.cc/club/AGENT"),
        InlineKeyboardButton("🌐 Перейти на наш сайт", url="https://poker-agent.org"),
    )
    await msg.answer(f"👋 Привет!, {msg.from_user.first_name}!\n\nДобро пожаловать!\n\nВыбери интересующий тебя пункт:", reply_markup=kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)