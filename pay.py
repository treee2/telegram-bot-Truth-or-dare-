import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types.message import ContentType
import conf

# log
logging.basicConfig(level=logging.INFO)

# prices
PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=100*100)  # в копейках (руб)

async def buy(message: types.Message, bot: Bot, aconf):
    if conf.PAYMENT_API.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Подписка на бота❤",
                           description="Поддержать разработчиков",
                           provider_token=conf.PAYMENT_API,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")

async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

async def successful_payment(message: types.Message, bot: Bot):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")

def register_payment_handlers(dp: Dispatcher, bot: Bot, aconf):
    dp.register_message_handler(lambda message: buy(message, bot, conf), commands=['buy'])
    dp.register_pre_checkout_query_handler(lambda query: pre_checkout_query(query, bot))
    dp.register_message_handler(lambda message: successful_payment(message, bot), content_types=ContentType.SUCCESSFUL_PAYMENT)

