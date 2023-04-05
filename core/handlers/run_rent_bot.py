import asyncio
import logging
from asyncio import AbstractEventLoop, CancelledError, Task, get_running_loop
from contextvars import Context
from typing import Any, Awaitable, Dict, List, Optional

from aiogram import Bot
from aiogram.dispatcher.dispatcher import DEFAULT_BACKOFF_CONFIG, Dispatcher
from aiogram.types import User
from aiogram.utils.backoff import BackoffConfig

logger = logging.getLogger(__name__)


class BotsManager:
    def __init__(self):
        self.collection_tasks: Dict[int, Task] = {}

    def _create_client_bot_task(
        self,
        dp: Dispatcher,
        bot: Bot,
        polling_timeout: int,
        handle_as_tasks: bool,
        backoff_config: BackoffConfig,
        allowed_updates: Optional[List[str]],
        **kwargs: Any,
    ) -> Any:
        return lambda: asyncio.create_task(
            self._start_client_bot(
                dp=dp,
                bot=bot,
                polling_timeout=polling_timeout,
                handle_as_tasks=handle_as_tasks,
                backoff_config=backoff_config,
                allowed_updates=allowed_updates,
                **kwargs,
            )
        )

    def start_client_bot(
        self,
        dp: Dispatcher,
        bot: Bot,
        polling_timeout: int = 10,
        handle_as_tasks: bool = True,
        backoff_config: BackoffConfig = DEFAULT_BACKOFF_CONFIG,
        allowed_updates: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        loop: AbstractEventLoop = get_running_loop()
        loop.call_soon(
            self._create_client_bot_task(
                dp=dp,
                bot=bot,
                polling_timeout=polling_timeout,
                handle_as_tasks=handle_as_tasks,
                backoff_config=backoff_config,
                allowed_updates=allowed_updates,
                **kwargs,
            ),
            context=Context(),
        )

    async def _start_client_bot(
        self,
        dp: Dispatcher,
        bot: Bot,
        polling_timeout: int = 10,
        handle_as_tasks: bool = True,
        backoff_config: BackoffConfig = DEFAULT_BACKOFF_CONFIG,
        allowed_updates: Optional[List[str]] = None,
        on_bot_startup: Optional[Awaitable] = None,
        on_bot_shutdown: Optional[Awaitable] = None,
        **kwargs: Any,
    ) -> Any:
        logger.info("Приступаем к запуску бота")
        client_bot: User = await bot.me()
        if on_bot_startup:
            await on_bot_startup

        try:
            logger.info(f'Запускаем бота {client_bot.username} {bot.id} {client_bot.full_name}.')
            client_bot_task = asyncio.create_task(
                dp._polling(
                    bot=bot,
                    handle_as_tasks=handle_as_tasks,
                    polling_timeout=polling_timeout,
                    backoff_config=backoff_config,
                    allowed_updates=allowed_updates,
                    **kwargs,
                )
            )
            self.collection_tasks[bot.id] = client_bot_task
            await client_bot_task
        except CancelledError:
            logger.info("Работа бота отменена.")
        finally:
            logger.info(f'Бот {client_bot.username} {bot.id} {client_bot.full_name} остановлен.')
            if on_bot_shutdown:
                await on_bot_shutdown

            await bot.session.close()

    def stop_client_bot(self, bot_id: int):
        task = self.collection_tasks.pop(bot_id)
        task.cancel()
