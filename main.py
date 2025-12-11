import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import asyncio

API_TOKEN = "8380762587:AAFv08YHY6_FUqwH1OTOlSv-qzhwiI6Y5pA"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------- КНОПКИ ----------
menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📱 Посчитать количество номеров", callback_data="count_numbers")],
    [InlineKeyboardButton(text="🔁 Проверить повторяющиеся юзеры", callback_data="check_duplicates")],
    [InlineKeyboardButton(text="📊 Отсортировать по количеству номеров", callback_data="sort_users")],
])

# Храним состояние — какой режим включён у пользователя
user_mode = {}

# ---------- СТАРТ ----------
@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Выбери действие:", reply_markup=menu)

# ---------- ОБРАБОТКА КНОПОК ----------
@dp.callback_query()
async def callbacks(callback):
    user_id = callback.from_user.id

    if callback.data == "count_numbers":
        user_mode[user_id] = "count"
        await callback.message.answer("📱 Отправь текст, я посчитаю количество номеров.")

    if callback.data == "check_duplicates":
        user_mode[user_id] = "duplicates"
        await callback.message.answer("🔁 Отправь список, я проверю повторяющиеся юзеры.")

    if callback.data == "sort_users":
        user_mode[user_id] = "sort"
        await callback.message.answer("📊 Отправь список, я отсортирую по количеству номеров.")

    await callback.answer()

# ---------- ОБРАБОТКА ТЕКСТА ----------
@dp.message(F.text)
async def process_text(msg: Message):
    user_id = msg.from_user.id
    mode = user_mode.get(user_id)

    if not mode:
        await msg.answer("Выбери команду:", reply_markup=menu)
        return

    text = msg.text

    # --- ФУНКЦИЯ 1: ПОСЧИТАТЬ НОМЕРА ---
    if mode == "count":
        numbers = re.findall(r"\+77\d{9}", text)
        await msg.answer(f"📱 Найдено номеров: **{len(numbers)}**", parse_mode=ParseMode.MARKDOWN)

    # --- ФУНКЦИЯ 2: ПОИСК ДУБЛИКАТОВ ЮЗЕРОВ ---
    elif mode == "duplicates":
        users = re.findall(r"@\w+", text)
        duplicates = [u for u in set(users) if users.count(u) > 1]

        if duplicates:
            await msg.answer("🔁 Найдены повторяющиеся юзеры:\n" + "\n".join(duplicates))
        else:
            await msg.answer("✅ Дубликатов нет.")

    # --- ФУНКЦИЯ 3: СОРТИРОВКА ПО КОЛИЧЕСТВУ НОМЕРОВ ---
    elif mode == "sort":
        blocks = text.strip().split("\n\n")

        data = {}

        for block in blocks:
            lines = block.strip().split("\n")
            username = lines[0].strip()
            nums = [n.strip() for n in lines[1:] if n.strip().startswith("+")]
            data[username] = nums

        sorted_users = sorted(data.items(), key=lambda x: len(x[1]), reverse=True)

        result = ""

        for user, nums in sorted_users:
            result += f"{user}\n"
            for n in nums:
                result += f"{n}\n"
            result += "\n"

        await msg.answer(result)

    # Сброс режима
    user_mode[user_id] = None


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
