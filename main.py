import asyncpg
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from aiogram.dispatcher.filters.command import CommandStart, Command
from core.handlers.basic import add_new_user
from core.handlers.basic import get_referrals, get_balance, set_sum, cancel_refill, request_balance, get_sum_out, \
    get_details, request_balance_complete, get_bid
from aiogram.dispatcher.filters import Text, ContentTypesFilter

from aiogram.types import ContentType
from aiogram.dispatcher.fsm.storage.memory import SimpleEventIsolation

from core.middleware.db_middleware import DbSession
from core.other.commands_bot import set_commands
from core.handlers.balance import get_sum, precheck, buy_complete
from core.utils.states import Steps
from core.handlers.dice import dice
from core.handlers.rent_bot import start_rent, start_rent_token, get_token, get_percent, get_youkassa_token, \
    pre_check_rent_bot, buy_complete_rent_bot
from core.handlers.run_rent_bot import BotsManager

from core.settings import settings

#asyncio.set_event_loop(asyncio.WindowsSelectorEventLoopPolicy())

logger = logging.getLogger(__name__)


async def start_bot(bot: Bot):
    await set_commands(bot)
    msg = 'Бот запущен!'
    await bot.send_message(settings.bots.admin_id, text=msg)


async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text='Бот выключен!')


async def create_pool(user, password, database, host):
    return await asyncpg.create_pool(user=user, password=password, database=database,
                                     host=host, port=5432, command_timeout=60)


async def start():
    logging.basicConfig(
        level=logging.INFO
    )
    bot = Bot(settings.bots.bot_token, parse_mode='HTML')
    storage = RedisStorage.from_url(settings.db.redis)
    dp = Dispatcher(events_isolation=SimpleEventIsolation(), storage=storage)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    job_stores = {
        'default': RedisJobStore(jobs_key='dispatched_trips_jobs',
                                 run_times_key='dispatched_trips_running',
                                 host='localhost',
                                 db=2,
                                 port=6379)
    }

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone='Europe/Moscow', jobstores=job_stores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)

    pooling = await create_pool(settings.db.user, settings.db.password, settings.db.db, settings.db.host)
    dp.callback_query.middleware(DbSession(pooling))
    dp.message.middleware(DbSession(pooling))
    dp.message.register(add_new_user, CommandStart())
    dp.message.register(get_balance, Text(text='Баланс'))
    dp.message.register(get_referrals, Text(text='Рефералы'))
    dp.callback_query.register(set_sum, F.data == 'refillbalance')
    dp.message.register(get_sum, Steps.GET_SUM)
    dp.pre_checkout_query.register(pre_check_rent_bot, Steps.GET_PAYMENTS)
    dp.message.register(buy_complete_rent_bot, ContentTypesFilter(content_types=[ContentType.SUCCESSFUL_PAYMENT]),
                        Steps.GET_PAYMENTS)
    dp.pre_checkout_query.register(precheck)
    dp.message.register(buy_complete, ContentTypesFilter(content_types=[ContentType.SUCCESSFUL_PAYMENT]))
    dp.callback_query.register(cancel_refill, F.data == 'cancelrefill')
    dp.callback_query.register(request_balance, F.data == 'requestbalance')
    dp.message.register(get_sum_out, Steps.GET_SUM_OUT)
    dp.message.register(get_details, Steps.GET_DETAILS)
    dp.callback_query.register(request_balance_complete, F.data.regexp(r'requestbalancecomplete'))
    dp.message.register(get_bid, Text(text='Играть'))
    dp.message.register(dice, Steps.GET_BID)
    dp.message.register(start_rent, Command(commands='rent_bot'))
    dp.callback_query.register(start_rent_token, F.data == 'youready')
    dp.message.register(get_token, Steps.GET_TOKEN)
    dp.message.register(get_percent, Steps.GET_PERCENT)
    dp.message.register(get_youkassa_token, Steps.GET_YOUKASSA_TOKEN)



    scheduler.start()
    bot_manager = BotsManager()
    await dp.start_polling(bot, dp_client_bot=dp, bot_manager= bot_manager)


if __name__ == "__main__":
    asyncio.run(start())
