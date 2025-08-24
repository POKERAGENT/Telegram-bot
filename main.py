import os
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- Настройки и переменные ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # ID администратора
WEBHOOK_URL = os.getenv("WEBHOOK")
DATABASE_URL = os.getenv("DATABASE_URL")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения!")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не найден в переменных окружения!")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
app = web.Application()

# --- Подключение к базе ---
async def create_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                name TEXT,
                username TEXT
            )
        """)

# --- Работа с базой ---
async def add_user(pool, user_id, name, username):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (id, name, username)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO UPDATE SET name = $2, username = $3
        """, user_id, name, username)

async def get_users_count(pool):
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users")

async def get_all_users(pool):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT id, name, username FROM users ORDER BY id")

# --- Хэндлер приветствия ---
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await add_user(app["db_pool"], msg.from_user.id, msg.from_user.first_name, msg.from_user.username)

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📲 Перейти в сообщество", url="https://t.me/+ji-5MkKSIodkODE6"),
        InlineKeyboardButton("🌐 Наш сайт", url="https://poker-agent.org"),
        InlineKeyboardButton("📝 NUTS POKER - утроим депозит", url="https://nutspoker.cc/club/AGENT"),
        InlineKeyboardButton("📝 QQPK POKER - утроим депозит", url="https://qqpk8.app:51999?shareCode=MGACZ9"),
        InlineKeyboardButton("📝 POKERDOM +3000rub на ваш счет", url="https://5pd-stat.com/click/6875327e6bcc63790e5beb28/1786/16153/subaccount"),
        InlineKeyboardButton("📝 ACR +50$ на ваш счет", url="https://go.wpnaffiliates.com/visit/?bta=236750&nci=5378"),
        InlineKeyboardButton("📝 TON POKER +30% Рейкбэк", url="https://t.me/myTonPokerBot/lobby?startapp=eyJhZnAiOiJZalZtTlRWak9UWmpObVExWkRZeFlqa3dOV1V3WWpkbFl6YzRPVGt5T1dVIn0"),
        InlineKeyboardButton("📝 1WIN +30% Рейкбэк", url="https://1wsmhl.life/?p=lu27"),
        InlineKeyboardButton("📝 RPTBET +20% Рейкбэк", url="https://click.rptbet.org/PaneSU76"),
        InlineKeyboardButton("📝 PHENOMPOKER +Призы/Розыгрыши", url="https://play.phenompoker.com/register?r=Agent"),
    )
    text = (f"<b>👋 Привет, {msg.from_user.first_name}!</b>\n\n"
            f"<b>Добро пожаловать!</b>\n\n"
            f"<b>Здесь собраны самые выгодные предложения для игроков:</b>\n\n"
            f"💰 эксклюзивные бонусы при регистрации!\n"
            f"🎁 бонусы на депозиты!\n"
            f"♻️ дополнительный рейкбэк!\n"
            f"📈 доступ к закрытым акциям и сообществу!\n\n"
            f"ℹ️ С подробными условиями каждого предложения, новостями и розыгрышами вы можете ознакомиться в нашем сообществе или на сайте в разделе АКЦИИ.\n\n"
            f"<b>Выберите интересующий вас пункт:👇</b>")
    await msg.answer(text, reply_markup=kb, parse_mode="HTML")

# --- Админка ---
@dp.message_handler(commands=["admin"])
async def admin_panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("📤 Рассылка", callback_data="broadcast"),
        InlineKeyboardButton("👥 Пользователи", callback_data="users")
    )
    await msg.answer("🔧 Админ-панель:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "stats")
async def send_stats(callback: types.CallbackQuery):
    count = await get_users_count(app["db_pool"])
    await callback.message.answer(f"📊 Всего пользователей в базе: {count}")

@dp.callback_query_handler(lambda c: c.data == "users")
async def list_users(callback: types.CallbackQuery):
    rows = await get_all_users(app["db_pool"])
    if not rows:
        await callback.message.answer("❌ Пользователей пока нет.")
        return

    text = "👥 <b>Список пользователей:</b>\n\n"
    for user in rows:
        user_id, name, username = user
        username_display = f"@{username}" if username else "—"
        text += f"<b>ID:</b> {user_id} | <b>Имя:</b> {name} | <b>Username:</b> {username_display}\n"

    for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        await callback.message.answer(chunk, parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == "broadcast")
async def start_broadcast(callback: types.CallbackQuery):
    await callback.message.answer("✏️ Введите текст рассылки:")
    dp.register_message_handler(send_broadcast, lambda m: m.from_user.id == ADMIN_ID, state=None)

async def send_broadcast(msg: types.Message):
    rows = await get_all_users(app["db_pool"])
    count = 0
    for user_id, _, _ in rows:
        try:
            await bot.send_message(user_id, msg.text)
            count += 1
        except:
            pass
    await msg.answer(f"✅ Сообщение отправлено {count} пользователям.")
    dp.message_handlers.unregister(send_broadcast)

# --- Webhook ---
async def on_startup(app):
    if not WEBHOOK_URL:
        raise ValueError("❌ WEBHOOK не найден в переменных окружения!")
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")

    app["db_pool"] = await create_db_pool()
    await init_db(app["db_pool"])

async def handle_request(request):
    if request.method == "POST":
        update = types.Update(**await request.json())
        Dispatcher.set_current(dp)
        Bot.set_current(bot)
        await dp.process_update(update)
    return web.Response(text="OK")

app.router.add_post("/webhook", handle_request)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    print(f"🚀 Запуск приложения на порту {port}...")
    try:
        web.run_app(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")