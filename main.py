import asyncio
from pathlib import Path
import logging
import betterlogging as bl

from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
    ip_filter_middleware,
)
from aiogram.webhook.security import IPFilter
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, F

from aiohttp.web_runner import GracefulExit
from aiohttp import web

from infrastructure.api.web_app_routes import setup_web_app_routes
from infrastructure.database.repo.requests import Database
from infrastructure.database.setup import create_engine, create_session_pool
from bot.config_reader import Config, load_config
from bot.handlers import routers_list

from bot.middlewares.database import DatabaseMiddleware
from bot.misc.default_commands import set_default_commands
from bot.services import broadcaster


async def on_startup(bot: Bot, config: Config, dp: Dispatcher) -> None:
    if config.tg_bot.use_webhook:
        await set_webhook(bot, dp, config)
    await broadcaster.broadcast(bot, config.tg_bot.admins_ids, "Bot started!")
    await set_default_commands(bot, config.tg_bot.admins_ids)


async def on_shutdown():
    # Although it will through an exception, I couldn't find any better workaround
    # But it does it fact gracefully shutdowns aiohttp server, we just do nothing on clenup,
    # since polling already stopped.
    raise GracefulExit()


async def start_dp_polling(bot: Bot, dp: Dispatcher) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def setup_dp_polling(app: web.Application):
    bot: Bot = app["bot"]
    dp: Dispatcher = app["dp"]
    asyncio.create_task(start_dp_polling(bot, dp))

    yield
    # as docs says: "aiohttp guarantees that cleanup code is called if and only if startup code was successfully finished."
    # in case of polling it doesn't really work. So we gotta call shutdown manually.
    # That's why we set dp.shutdown.register(on_shutdown)


async def set_webhook(bot: Bot, dp: Dispatcher, config: Config) -> None:
    me = await bot.get_me()
    url = f"{config.web.domain}{config.tg_bot.webhook_path}"
    logging.info(
        f"Run webhook for bot https://t.me/{me.username} "
        f'id={bot.id} - "{me.full_name}" on {url}'
    )
    await bot.set_webhook(
        url=url,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
        secret_token=config.tg_bot.webhook_secret,
    )


def register_global_middlewares(
    dp: Dispatcher,
    session_pool,
):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    dp.message.outer_middleware(DatabaseMiddleware(session_pool))


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")
    return logger


def main():
    logger = setup_logging()

    config = load_config(".env")
    if config.tg_bot.use_redis:
        # TODO: Move this import to the top if you use Redis
        from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

        storage = RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        storage = MemoryStorage()

    bot = Bot(
        token=config.tg_bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    engine = create_engine(
        f"sqlite+aiosqlite:///{Path(__file__).parent.resolve()}/data/main.db"
    )
    db = Database(engine)
    dp = Dispatcher(storage=storage)
    asyncio.run(db.create_tables())
    session_pool = create_session_pool(engine)

    dp.include_routers(*routers_list)

    register_global_middlewares(dp, session_pool)

    dp.workflow_data.update(
        config=config,
        dp=dp,
    )

    dp.message.filter(F.chat.type == "private")  # work only in private chats

    dp.startup.register(on_startup)

    app = web.Application()
    app["bot"] = bot
    app["config"] = config
    app["session_pool"] = session_pool

    web_app = web.Application()
    web_app["bot"] = bot
    web_app["config"] = config
    web_app["web_app_name"] = config.tg_bot.web_app_name
    web_app["session_pool"] = session_pool
    # If you use redis you can pass it to web_app
    # pool = ConnectionPool.from_url(config.redis.make_connection_string())
    # redis = Redis(connection_pool=pool)
    # web_app["redis"] = redis
    setup_web_app_routes(web_app)
    app.add_subapp(f"/{config.tg_bot.web_app_name}", web_app)

    if config.tg_bot.use_webhook:
        ip_filter_middleware(ip_filter=IPFilter.default())

        webhook_request_handler = SimpleRequestHandler(
            dispatcher=dp, bot=bot, secret_token=config.tg_bot.webhook_secret
        )

        webhook_request_handler.register(app, path=config.tg_bot.webhook_path)
        setup_application(app, dp, bot=bot)
    else:
        dp.shutdown.register(
            on_shutdown
        )  # we should register GracefulExit for aiohttp server if we run polling
        app["dp"] = dp
        app.cleanup_ctx.append(setup_dp_polling)

    logger.info(f"Running app on {config.web.host}:{config.web.port}")
    web.run_app(app, host=config.web.host, port=config.web.port)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
