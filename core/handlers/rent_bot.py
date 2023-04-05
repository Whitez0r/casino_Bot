from aiogram.types import Message, CallbackQuery
from core.keyboars.inline import you_ready
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram import Bot, Dispatcher
from core.utils.states import Steps
from core.other.db_connect import Request
from aiogram.types import LabeledPrice, PreCheckoutQuery
from datetime import datetime, timedelta
from core.handlers.run_rent_bot import BotsManager
from core.other.commands_bot import set_commands


async def buy_complete_rent_bot(message: Message, state: FSMContext, request: Request, dp_client_bot: Dispatcher, bot_manager: BotsManager):
    data = await state.get_data()
    token: str = data['bot_token']
    bot_id: int = int(str(token.split(':')[0]))
    you_kassa: str = data['youkassa_token']
    percent: str = data['percent']
    payment_data: str = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S")

    get_run_bot = await request.set_new_bot(bot_id, token, message.from_user.id, you_kassa, payment_data, percent )

    if get_run_bot:
        await message.answer(f'Оплата получена. Твой бот будет запущен немедленно.')
        await run_bot(message.from_user.id, token, dp_client_bot, bot_manager)
    else:
        await message.answer(f'Оплата получена. Аренда продлена.')

    await state.clear()

async def start_bot(bot: Bot, admin_id):
    await set_commands(bot)
    msg = 'Бот запущен!'
    await bot.send_message(admin_id, text=msg)

async def stop_bot(bot: Bot, admin_id):
    await set_commands(bot)
    msg = 'Бот остановлен!'
    await bot.send_message(admin_id, text=msg)

async def run_bot(user_id, token, dp_client_bot: Dispatcher, bot_manager: BotsManager):
    try:
        bot = Bot(token)

        if bot.id in bot_manager.collection_tasks:
            return

        bot_manager.start_client_bot(
            dp=dp_client_bot,
            bot=bot,
            on_bot_startup=start_bot(bot, user_id),
            on_bot_shutdown=stop_bot(bot, user_id)
        )
    except:
        pass

async def pre_check_rent_bot(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def get_youkassa_token(message: Message, bot: Bot, state: FSMContext, request: Request):
    await state.update_data(youkassa_token=message.text)
    youkassa_token = await request.get_youkassa_token(bot.id)
    #price = [LabeledPrice(label='Аренда бота казино', amount=500)]
    price = [LabeledPrice(label='Сумма пополнения', amount=500 * 100)]
    print(price)
    title = ' оплата за аренду бота whitez0r'
    description = 'Арендуй бота и начни зарабатывать прямо сейчас'
    await bot.send_invoice(chat_id=message.chat.id,
                           title=title,
                           description=description,
                           payload='casino',
                           provider_token=youkassa_token,
                           currency='rub',
                           prices=price)
    await state.set_state(Steps.GET_PAYMENTS)



async def get_percent(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(f'{message.text} - это похоже на число')
        return

    await state.update_data(percent=message.text)
    await message.answer('Теперь отправь Юкасса токен')
    await state.set_state(Steps.GET_YOUKASSA_TOKEN)

async def get_token(message: Message, state: FSMContext):
    await state.update_data(bot_token=message.text)
    await message.answer('Теперь отправь процент рефералам')
    await state.set_state(Steps.GET_PERCENT)

async def start_rent_token(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.answer_callback_query(call.id)
    await call.message.edit_text('Начинаем процедуру аренды бота', reply_markup=None)
    await call.message.answer(f'Отпрвь токен своего бота')
    await state.set_state(Steps.GET_TOKEN)

async def start_rent(message: Message):
    await message.answer(f'Ок, начинаем оформлять процедуру аренды бота.\r\n'
                         f'Подготовь следующие данные:\r\n'
                         f'1) Токен бота. Зарегестрируй своего бота через @botfather\r\n'
                         f'2) Процент отчисления рефералам \r\n'
                         f'3) Юкасса токен. Добавь платежный шлюз для своего бота в том же @botfather\r\n'
                         f'4) Оплата. Я вышлю тебе счет для оплаты аренды бота на месяц\r\n\r\n'
                         
                         f'Как будешь готов жми кнопку', reply_markup=you_ready)