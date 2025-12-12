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
    [InlineKeyboardButton(text="Посчитать количество номеров", callback_data="count_numbers")],
    [InlineKeyboardButton(text="Проверить повторяющиеся юзеры", callback_data="check_duplicates")],
    [InlineKeyboardButton(text="Проверить повторяющиеся номера", callback_data="check_phone_duplicates")],
    [InlineKeyboardButton(text="Отсортировать по количеству номеров", callback_data="sort_users")],
    [InlineKeyboardButton(text="Сделать отчёт", callback_data="make_report")],
    [InlineKeyboardButton(text="Отчёт (Субботний прайс)", callback_data="make_report_saturday")],
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
        await callback.message.answer(".")

    if callback.data == "check_duplicates":
        user_mode[user_id] = "duplicates"
        await callback.message.answer(".")

    if callback.data == "sort_users":
        user_mode[user_id] = "sort"
        await callback.message.answer(".")

    if callback.data == "check_phone_duplicates":
        user_mode[user_id] = "phone_dupl"
        await callback.message.answer(".")

    if callback.data == "make_report":
        user_mode[user_id] = "report"
        await callback.message.answer(".")

    if callback.data == "make_report_saturday":
        user_mode[user_id] = "report_saturday"
        await callback.message.answer(".")

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

    # --- 2. ДУБЛИ ЮЗЕРОВ ---
    elif mode == "duplicates":
        users = re.findall(r"@\w+", text)
        duplicates = [u for u in set(users) if users.count(u) > 1]
        await msg.answer(
            "🔁 Найдены повторяющиеся юзеры:\n" + "\n".join(duplicates)
            if duplicates else "✅ Дубликатов нет."
        )

    # --- 3. ДУБЛИ НОМЕРОВ ---
    elif mode == "phone_dupl":
        nums = re.findall(r"\+77\d{9}", text)
        duplicates = [n for n in set(nums) if nums.count(n) > 1]
        await msg.answer(
            "📞 Найдены повторяющиеся номера:\n" + "\n".join(duplicates)
            if duplicates else "✅ Повторяющихся номеров нет."
        )

    # --- 4. СОРТИРОВКА ---
    elif mode == "sort":
        blocks = text.strip().split("\n\n")
        data = {}

        for block in blocks:
            lines = block.strip().split("\n")
            username = lines[0]
            nums = [l for l in lines[1:] if l.startswith("+")]
            data[username] = nums

        result = ""
        for u, n in sorted(data.items(), key=lambda x: len(x[1]), reverse=True):
            result += u + "\n" + "\n".join(n) + "\n\n"

        await msg.answer(result)

    # --- 5. ОБЫЧНЫЙ ОТЧЁТ ---
    elif mode == "report":
        await msg.answer(make_report(text, saturday=False))

    # --- 6. СУББОТНИЙ ОТЧЁТ ---
    elif mode == "report_saturday":
        await msg.answer(make_report(text, saturday=True))

    user_mode[user_id] = None


# ---------- ФУНКЦИЯ ОТЧЁТА ----------
def make_report(text, saturday=False):
    blocks = text.strip().split("\n\n")
    report = "ОТЧЕТ БХ(25 мин)\n\n"

    for block in blocks:
        lines = block.strip().split("\n")
        raw_user = lines[0]

        po5 = "по 5" in raw_user.lower()
        po3 = "по 3" in raw_user.lower()

        username = raw_user.replace("по 5", "").replace("по 3", "").strip()
        nums = [l for l in lines[1:] if l.startswith("+")]
        count = len(nums)

        if count == 0:
            price = 0
        else:
            if saturday:
                price = count * (3 if po3 else 4)
            else:
                if po5:
                    price = count * 5
                elif count >= 5:
                    price = count * 6
                else:
                    price = count * 5.5

        report += f"{username} {price}$\n"
        for n in nums:
            report += n + "\n"
        report += "\n"

    report += "Обменники @odmenikk, @kill_monger_3 и @swhexs"
    return report


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
