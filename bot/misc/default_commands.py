from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault


async def set_default_commands(bot: Bot, admins_ids: list[int]) -> None:
    commands_users = {
        "start": "Start command",
        "inline_web_app": "Launch web app from inline button",
        "reply_web_app": "Launch web app from reply button",
        "rm_reply_web_app": "Remove reply button",
    }

    commands_admins = {
        "admin": "Admin command",
        **commands_users,
    }

    await bot.set_my_commands(
        [
            BotCommand(command=name, description=value)
            for name, value in commands_users.items()
        ],
        scope=BotCommandScopeDefault(),
    )

    for admin_id in admins_ids:
        await bot.set_my_commands(
            [
                BotCommand(command=name, description=value)
                for name, value in commands_admins.items()
            ],
            scope=BotCommandScopeChat(chat_id=admin_id),
        )
