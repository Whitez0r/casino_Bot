from aiogram.types import Message
from aiogram import Bot
from aiogram.dispatcher.filters import CommandObject
from core.other.db_connect import Request
from core.keyboars.reply import keyboard_user
from core.keyboars.inline import keyboard_balance
from aiogram.types import CallbackQuery
from aiogram.dispatcher.fsm.middleware import FSMContext
from core.keyboars.inline import cancel_redill_keyboard, keyboard_for_admin
from core.utils.states import Steps


async def get_bid(message: Message, state: FSMContext):
    await message.answer('Введите свою ставку.')
    await state.set_state(Steps.GET_BID)


async def request_balance_complete(call: CallbackQuery, bot: Bot, request: Request):
    await bot.answer_callback_query(call.id)
    user_id = call.data.split('|')[1]
    sum_out = call.data.split('|')[2]

    await request.refill_balance(user_id, bot.id, int(sum_out) * -1)
    await bot.send_message(user_id, f'Произведена выплата баланса по твоей заявке.')
    await call.message.edit_text('Выплата обработана.', reply_markup=None)


async def get_details(message: Message, bot: Bot, request: Request, state: FSMContext):
    details = message.text
    data = await state.get_data()
    get_sum = data.get('get_sum')
    current_balance = data.get('curbalance')

    message_for_admin = f'Пользователь {message.from_user.id}, {message.from_user.first_name} ' \
                        f'подал заявку на вывод баланса. \r\n' \
                        f'Сумма - {get_sum}\r\n' \
                        f'Реквизиты - {details}\r\n' \
                        f'Баланс - {current_balance}'

    admin_id = await request.get_admin_id(bot.id)

    await bot.send_message(admin_id, message_for_admin, reply_markup=keyboard_for_admin(message.from_user.id,
                                                                                        get_sum))

    await message.answer(f'Твоя заявка на выплату принята. Ожидайте уведомления.')
    await state.clear()


async def get_sum_out(message: Message, bot: Bot, request: Request, state: FSMContext):
    get_sum = message.text
    if not get_sum.isdigit():
        await message.answer(f'{get_sum} - это не очень-то похоже на число. Попробуй еще раз.')
        return

    current_balance = await request.get_balance(message.from_user.id, bot.id)
    if current_balance < int(get_sum):
        await message.answer(f'{get_sum} - это больше, чем твой текущий баланс. Введите сумму меньше {current_balance}р,')
        return

    await state.update_data(get_sum=get_sum, curbalance=current_balance)
    await message.answer(f'Теперь укажите реквизиты на которые хочешь вывести указанную сумму.')
    await state.set_state(Steps.GET_DETAILS)


async def request_balance(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.answer_callback_query(call.id)
    await call.message.edit_text(f'Укажите сумму для вывода')
    await state.set_state(Steps.GET_SUM_OUT)


async def cancel_refill(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.answer_callback_query(call.id)
    await call.message.edit_text(f'Пополнение баланса отменено', reply_markup=None)
    await state.clear()


async def set_sum(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.answer_callback_query(call.id)
    await call.message.answer(f'Введите сумму пополнени. От 100 до 900р.', reply_markup=cancel_redill_keyboard)
    await state.set_state(Steps.GET_SUM)


async def add_new_user(message: Message, bot: Bot, command: CommandObject, request: Request):
    referral = command.args
    await request.add_new_user(message.from_user.id, message.from_user.username, message.from_user.first_name,
                               bot.id, 0, referral)
    text_answer = f'Привет, {message.from_user.first_name}!' \
                  f'Рады видеть тебя в нашем казино. Играй и выигрывай миллионы!\r\n' \
                  f'Твоя реферальная ссылка:\r\n' \
                  f'https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}'
    await message.answer(text_answer, reply_markup=keyboard_user)


async def get_balance(message: Message, bot: Bot, request: Request):
    balance = await request.get_balance(message.from_user.id, bot.id)
    await message.answer(f'Твой баланс равен {balance}p.', reply_markup=keyboard_balance)


async def get_referrals(message: Message, bot: Bot, request: Request):
    referrals = await request.get_referrals(message.from_user.id, bot.id)

    if referrals != '':
        text = f'Вот твои рефералы:\r\n{referrals}'
    else:
        text = 'Рефералов не найдено'
    await message.answer(text)
