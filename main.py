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
    [InlineKeyboardButton(text="📞 Проверить повторяющиеся номера", callback_data="check_phone_duplicates")],
    [InlineKeyboardButton(text="📊 Отсортировать по количеству номеров", callback_data="sort_users")],
    [InlineKeyboardButton(text="💰 Сделать отчёт", callback_data="make_report")],
])

# Храним режим пользователя
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
        await callback.message.answer("🔁 Отправь список, я проверю повторяющихся юзеров.")

    if callback.data == "sort_users":
        user_mode[user_id] = "sort"
        await callback.message.answer("📊 Отправь список, я отсортирую по количеству номеров.")

    if callback.data == "check_phone_duplicates":
        user_mode[user_id] = "phone_dupl"
        await callback.message.answer("📞 Отправь список, я найду повторяющиеся номера телефона.")

    if callback.data == "make_report":
        user_mode[user_id] = "report"
        await callback.message.answer("💰 Отправь список юзеров с номерами, я сделаю отчёт.")

    await callback.answer()

# ---------- ОБРАБОТКА ТЕКСТА ----------
@dp.message(F.text)
async def process_text(msg: Message):
    user_id = msg.from_user.id
    mode = user_mode.get(user_id)
    text = msg.text

    if not mode:
        await msg.answer("Выбери действие:", reply_markup=menu)
        return

    # --- 1. ПОСЧИТАТЬ НОМЕРА ---
    if mode == "count":
        numbers = re.findall(r"\+77\d{9}", text)
        await msg.answer(f"📱 Найдено номеров: **{len(numbers)}**", parse_mode=ParseMode.MARKDOWN)

    # --- 2. Дубли юзеров ---
    elif mode == "duplicates":
        users = re.findall(r"@\w+", text)
        duplicates = [u for u in set(users) if users.count(u) > 1]
        if duplicates:
            await msg.answer("🔁 Найдены повторяющиеся юзеры:\n" + "\n".join(duplicates))
        else:
            await msg.answer("✅ Дубликатов нет.")

    # --- 3. Проверка повторяющихся номеров ---
    elif mode == "phone_dupl":
        nums = re.findall(r"\+77\d{9}", text)
        duplicates = [n for n in set(nums) if nums.count(n) > 1]

        if duplicates:
            await msg.answer("📞 Найдены повторяющиеся номера:\n" + "\n".join(duplicates))
        else:
            await msg.answer("✅ Повторяющихся номеров нет.")

    # --- 4. Сортировка по количеству ---
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

    # --- 5. СОЗДАНИЕ ОТЧЁТА ---
    elif mode == "report":

        blocks = text.strip().split("\n\n")
        report = "ОТЧЕТ БХ(25 мин)\n\n"

        for block in blocks:
            lines = block.strip().split("\n")
            username = lines[0].strip()

            # Проверка "по 5"
            fixed5 = "по 5" in username.lower()

            nums = [l.strip() for l in lines[1:] if l.startswith("+")]
            count = len(nums)

            if count == 0:
                price = 0
            else:
                if fixed5:
                    price = count * 5
                elif count >= 5:
                    price = count * 6
                else:
                    price = count * 5.5

            # Очистить имя при "по 5"
            username_clean = username.replace("по 5", "").strip()

            report += f"{username_clean} {price}$\n"
            for n in nums:
                report += n + "\n"
            report += "\n"

        # Добавить низ отчёта
        report += "Обменники @odmenikk, @kill_monger_3 и @swhexs"

        await msg.answer(report)

    user_mode[user_id] = None


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
