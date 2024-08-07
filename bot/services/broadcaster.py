import asyncio
import logging
from typing import Union

from aiogram import Bot
from aiogram import exceptions
from aiogram.types import InlineKeyboardMarkup

from typing import Any, Callable


async def send_telegram_action(bot_method: Callable[..., Any], *args, **kwargs):
    """
    Universal Telegram action sender.

    :param bot_method: Telegram Bot method to be called (e.g., bot.send_message).
    :param args: Positional arguments to pass to the bot method.
    :param kwargs: Keyword arguments to pass to the bot method.
    :return: success.
    """
    try:
        result = await bot_method(*args, **kwargs)
        logging.info(f"Target [ID:{kwargs.get('chat_id', 'unknown')}]: success")
        return result
    except exceptions.TelegramBadRequest:
        logging.error("Telegram server says - Bad Request: chat not found")
    except exceptions.TelegramForbiddenError:
        logging.error(
            f"Target [ID:{kwargs.get('chat_id', 'unknown')}]: got TelegramForbiddenError"
        )
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{kwargs.get('chat_id', 'unknown')}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        # Recursive call with the same bot method and parameters
        return await send_telegram_action(bot_method, *args, **kwargs)
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{kwargs.get('chat_id', 'unknown')}]: failed")


async def send_message(
    bot: Bot,
    user_id: Union[int, str],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
):
    return await send_telegram_action(
        bot.send_message,
        chat_id=user_id,
        text=text,
        disable_notification=disable_notification,
        reply_markup=reply_markup,
    )


async def broadcast(
    bot: Bot,
    users: list[Union[str, int]],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
) -> int:
    """
    Simple broadcaster.
    :param bot: Bot instance.
    :param users: List of users.
    :param text: Text of the message.
    :param disable_notification: Disable notification or not.
    :param reply_markup: Reply markup.
    :return: Count of messages.
    """
    count = 0
    try:
        for user_id in users:
            if await send_message(
                bot, user_id, text, disable_notification, reply_markup
            ):
                count += 1
            await asyncio.sleep(
                0.05
            )  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successful sent.")

    return count
