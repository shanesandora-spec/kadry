import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- КОНФІГУРАЦІЯ ---
TOKEN = "8856125392:AAHzbmwiy5H7wE1IVw3BM0qIivgbT1mEuRQ"
ADMIN_ID = "8319248273"
WORK_GROUP_LINK = "https://t.me/+Zg_AH9cFa9pkZWVi"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class HRForm(StatesGroup):
    exp = State()
    amount = State()
    guarantee = State()
    price = State()
    algo = State()
    contact = State()

# --- МЕНЮ ---
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ Про бота та вакансію", callback_data="about")],
        [InlineKeyboardButton(text="📩 Надіслати заявку", callback_data="apply")]
    ])

# --- ЛОГІКА СТАРТУ ---
@dp.message(Command("start"))
async def start(message: types.Message):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"👤 <b>Новий візит:</b> {user.full_name} (ID: {user.id})", parse_mode='HTML')
    
    text = (
        "<b>👋 Вітаю! Я — HR менеджер агенції Rost Reviews.</b>\n\n"
        "Ми займаємося управлінням репутацією та шукаємо відповідальних спеціалістів.\n"
        "Я допоможу вам пройти етап співбесіди максимально швидко та автоматизовано.\n\n"
        "🚀 <b>Чому з нами круто працювати:</b>\n"
        "• Стабільні обсяги завдань.\n"
        "• Прозора оплата за кожен відгук.\n"
        "• Повне навчання та підтримка 24/7.\n\n"
        "<i>Оберіть дію, щоб розпочати співпрацю:</i>"
    )
    await message.answer(text, reply_markup=get_main_menu(), parse_mode='HTML')

# --- ІНФО ---
@dp.callback_query(F.data == "about")
async def about(call: types.CallbackQuery):
    text = (
        "🤖 <b>Детальніше про бота та роботу:</b>\n\n"
        "Цей бот — ваш перший крок до стабільного заробітку. Ми спеціалізуємося на якісному управлінні репутацією брендів.\n\n"
        "📋 <b>Етапи роботи:</b>\n"
        "1. Заповнення анкети (через цього бота).\n"
        "2. Перевірка даних нашим HR-відділом.\n"
        "3. Отримання доступу до робочої групи.\n\n"
        "⚠️ <b>Важливо:</b> Ми цінуємо відповідальність та готові навчати тих, хто хоче працювати довгостроково."
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад до меню", callback_data="back")]]), parse_mode='HTML')

@dp.callback_query(F.data == "back")
async def back(call: types.CallbackQuery):
    await call.message.edit_text("👋 <b>Вітаю! Я — HR менеджер агенції Rost Reviews.</b>\n\nОберіть дію:", reply_markup=get_main_menu(), parse_mode='HTML')

# --- АНКЕТА (ПОВНИЙ ФУНКЦІОНАЛ) ---
@dp.callback_query(F.data == "apply")
async def start_apply(call: types.CallbackQuery, state: FSMContext):
    msg = await call.message.answer("📝 <b>Питання 1/6</b>\nЯкий у вас досвід роботи у сфері відгуків?", parse_mode='HTML')
    await state.update_data(last_msg=msg.message_id)
    await state.set_state(HRForm.exp)
    await call.message.delete()

async def ask_next(msg: types.Message, state: FSMContext, next_state: State, text: str, step: int):
    data = await state.get_data()
    try: await bot.delete_message(msg.chat.id, data['last_msg'])
    except: pass
    new_msg = await msg.answer(f"📝 <b>{step}/6</b> {text}", parse_mode='HTML')
    await state.update_data(last_msg=new_msg.message_id)
    await state.set_state(next_state)
    try: await msg.delete()
    except: pass

@dp.message(HRForm.exp)
async def q2(msg: types.Message, state: FSMContext):
    await state.update_data(exp=msg.text)
    await ask_next(msg, state, HRForm.amount, "Скільки відгуків на день ви зможете публікувати?", 2)

@dp.message(HRForm.amount)
async def q3(msg: types.Message, state: FSMContext):
    await state.update_data(amount=msg.text)
    await ask_next(msg, state, HRForm.guarantee, "Чи готові ви до гарантії публікації на 7 днів?", 3)

@dp.message(HRForm.guarantee)
async def q4(msg: types.Message, state: FSMContext):
    await state.update_data(guarantee=msg.text)
    await ask_next(msg, state, HRForm.price, "Яка ваша бажана оплата за один відгук?", 4)

@dp.message(HRForm.price)
async def q5(msg: types.Message, state: FSMContext):
    await state.update_data(price=msg.text)
    await ask_next(msg, state, HRForm.algo, "Чи знайомі ви з алгоритмами публікації відгуків?", 5)

@dp.message(HRForm.algo)
async def q6(msg: types.Message, state: FSMContext):
    await state.update_data(algo=msg.text)
    await ask_next(msg, state, HRForm.contact, "Ваш контактний Telegram або номер телефону:", 6)

@dp.message(HRForm.contact)
async def finish(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    user = msg.from_user
    report = (f"📩 <b>Нова анкета кандидата</b>\n\n"
              f"👤 Користувач: {user.full_name} (ID: {user.id})\n"
              f"🔸 Досвід: {data['exp']}\n🔸 Обсяг: {data['amount']}\n"
              f"🔸 Гарантія: {data['guarantee']}\n🔸 Оплата: {data['price']}\n"
              f"🔸 Алгоритми: {data['algo']}\n🔸 Контакт: {msg.text}")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Схвалити", callback_data=f"app_{msg.from_user.id}")],
        [InlineKeyboardButton(text="❌ Відмовити", callback_data=f"rej_{msg.from_user.id}")]
    ])
    
    await bot.send_message(ADMIN_ID, report, reply_markup=kb, parse_mode='HTML')
    await msg.answer("✅ <b>Дякуємо!</b> Ваша анкета успішно відправлена на розгляд. Очікуйте відповіді.", parse_mode='HTML')
    await state.clear()

# --- КНОПКИ АДМІНА ---
@dp.callback_query(F.data.startswith("app_"))
async def approve(call: types.CallbackQuery):
    c_id = call.data.split("_")[1]
    try:
        await bot.send_message(c_id, f"🎉 <b>Вітаємо! Вашу анкету схвалено.</b>\n\nПриєднуйтесь до робочої групи:\n{WORK_GROUP_LINK}", parse_mode='HTML')
        await call.message.edit_text(call.message.text + "\n\n✅ <b>СТАТУС: СХВАЛЕНО</b>", parse_mode='HTML')
    except Exception as e:
        await call.message.answer(f"❌ Помилка: {e}")
    await call.answer("Готово!")

@dp.callback_query(F.data.startswith("rej_"))
async def reject(call: types.CallbackQuery):
    c_id = call.data.split("_")[1]
    try:
        await bot.send_message(c_id, "⚠️ <b>Дякуємо за інтерес.</b> На даний момент ми не готові запропонувати співпрацю.", parse_mode='HTML')
        await call.message.edit_text(call.message.text + "\n\n❌ <b>СТАТУС: ВІДМОВЛЕНО</b>", parse_mode='HTML')
    except: pass
    await call.answer("Відмовлено!")

if __name__ == "__main__":
    app = Flask(__name__)
    Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(dp.start_polling(bot))
