import math

from aiogram import Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from core.other.db_connect import Request
from core.keyboars.inline import cancel_redill_keyboard


async def buy_complete(message: Message, bot: Bot, request: Request):
    refill_balance = message.successful_payment.total_amount // 100
    await request.refill_balance(message.from_user.id, bot.id, refill_balance)

    await message.answer(f'Твой баланс пополнен на {refill_balance}р.')

    referer = await request.get_referer(message.from_user.id, bot.id)

    if referer != 'None':
        percent_referral = await request.get_percent(bot.id)
        referer_balance = math.trunc(refill_balance / 100 * percent_referral)
        await request.refill_balance(referer, bot.id, referer_balance)
        user_info = f'{message.from_user.id} {message.from_user.username} {message.from_user.first_name}'
        await bot.send_message(referer, f'Тебе начислены реферальные за пользователя {user_info} в размере '
                                        f'{referer_balance}р.')


async def precheck(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def get_sum(message: Message, bot: Bot, state: FSMContext, request: Request):
    if not message.text.isdigit() or not (99 < int(message.text) < 901):
        await message.reply(f'Введите корректную сумму', reply_markup=cancel_redill_keyboard)
        return

    youkassa_token = await request.get_youkassa_token(bot.id)
    print(youkassa_token)
    price = [LabeledPrice(label='Сумма пополнения', amount=int(message.text) * 100)]
    print(price)
    title = 'Пополнение баланса казино.'
    description = 'Начните играть уже сейчас.'

    await bot.send_invoice(chat_id=message.chat.id,
                           title=title,
                           description=description,
                           payload='casino',
                           provider_token=youkassa_token,
                           currency='rub',
                           prices=price)
    await state.clear()
