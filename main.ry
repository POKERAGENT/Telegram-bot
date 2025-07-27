from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os

TOKEN = os.getenv("7996039687:AAG1lXXhiarZbj_4wD3mFscU4ZZzoUZsJ2U")

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
    await msg.answer(f"👋 Привет!, {name}!\n\nДобро пожаловать!\n\nВыбери интересующий тебя пункт:", reply_markup=kb)

if name == '__main__':
    executor.start_polling(dp, skip_updates=True)