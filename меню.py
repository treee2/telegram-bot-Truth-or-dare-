import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import random
import conf
import pay
import quension
import pinRules

# Initialize bot and dispatcher
bot = Bot(token=conf.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Register payment handlers
pay.register_payment_handlers(dp, bot, conf)  # главная ошибка не было этой строчки

# кнопка правил игры
pinRules.register_rules_handler(dp, bot)

# Logging
logging.basicConfig(level=logging.INFO) # может удалю тратит нужное пространтво на сервере

# Режимы и темы
modes = quension.modes
# Вопросы и действия
questions = quension.questions
actions = quension.actions
# Варианты напоминаний
reminders = quension.reminders

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Режим", callback_data='mode'),
        InlineKeyboardButton("Обр. связь по игре", callback_data='feedback'),
        InlineKeyboardButton("Правила игры", callback_data='rules'),
        InlineKeyboardButton("Поддержать", callback_data='support')
    ]
    keyboard.add(*buttons)
    await message.reply("Главное меню", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'mode')
async def show_modes(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(mode, callback_data=f"theme_{mode}") for mode in modes]
    keyboard.add(*buttons)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Выберите режим:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('theme_'))
async def show_themes(callback_query: types.CallbackQuery):
    mode = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(theme, callback_data=f"start_{theme}") for theme in modes[mode]]
    keyboard.add(*buttons)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Выберите тему:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('start_'))
async def start_game(callback_query: types.CallbackQuery):
    theme = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    context = dp.current_state(user=user_id)
    await context.update_data(theme=theme)
    await context.update_data(questions=questions[theme][:], actions=actions[theme][:])
    await show_question_action(callback_query)

async def show_question_action(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Правда", callback_data='truth'),
        InlineKeyboardButton("Действие", callback_data='dare'),
        InlineKeyboardButton("Меню", callback_data='menu')
    ]
    keyboard.add(*buttons)
    await bot.send_message(callback_query.from_user.id, "Выберите действие:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'truth')
async def truth(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    context = dp.current_state(user=user_id)
    data = await context.get_data()
    questions_list = data.get('questions', [questions])
    if not questions_list:
        await bot.send_message(callback_query.from_user.id, "Все вопросы закончились. Начните заново или выберите другую тему.")
        return
    question = random.choice(questions_list)  # Выбираем случайный вопрос
    questions_list.remove(question)  # Удаляем выбранный вопрос из списка
    await context.update_data(questions=questions_list)
    await bot.send_message(callback_query.from_user.id, f"Правда: {question}")
    await show_question_action(callback_query)

@dp.callback_query_handler(lambda c: c.data == 'dare')
async def dare(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    context = dp.current_state(user=user_id)
    data = await context.get_data()
    actions_list = data.get('actions', [])
    if not actions_list:
        await bot.send_message(callback_query.from_user.id, "Все действия закончились. Начните заново или выберите другую тему.")
        return
    action = random.choice(actions_list)  # Выбираем случайное действие
    actions_list.remove(action)  # Удаляем выбранное действие из списка
    await context.update_data(actions=actions_list)
    await bot.send_message(callback_query.from_user.id, f"Действие: {action}")
    await show_question_action(callback_query)

@dp.callback_query_handler(lambda c: c.data == 'menu')
async def menu(callback_query: types.CallbackQuery):
    await send_welcome(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'feedback')
async def feedback(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "По вопросам и предложениям писать разработчикам: @HTsunisshin")

# платеж 
@dp.callback_query_handler(lambda c: c.data == 'support')
async def support(callback_query: types.CallbackQuery):
    await pay.buy(callback_query.message, bot, conf)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
