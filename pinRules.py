from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher

async def rules(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(callback_query.from_user.id, '''
 ~ Правила стандарные для игры "Правда" или "Действие" бот предлагает выбрать режим и можно начинать играть
 ~ Когда вопросы или действия закончаться бот пришлёт об этом сообщение 
Игра с партнёром Правила:
 ~ Игроки сами выбирают кто будет начинать игру.
 ~ Игрок выбирает правду или действие.
 ~ Если игрок не отвечает или не выполняет свой выбор, то выбирает повторно с вероятностью ответа 100%. 
 ~ Игрок выполняет задание или отвечает на вопрос.
 ~ После выполнения задания или ответа на вопрос ход передаётся другому игроку.
 ~ Игра продолжается до тех пор, пока оба игрока хотят играть.
 ~ Надеюсь вам понравиться)''')

def register_rules_handler(dp: Dispatcher, bot: Bot):
    dp.register_callback_query_handler(lambda c: rules(c, bot), lambda c: c.data == 'rules')
