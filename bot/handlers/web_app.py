from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)
from aiogram.types import Message

from bot.config_reader import Config


web_app_router = Router()


@web_app_router.message(Command("inline_web_app"))
async def user_inline_web_app(message: Message, bot: Bot, config: Config):
    bot_info = await bot.get_me()
    await message.answer(
        "Launch web app from inline button!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Launch!",
                        url=f"https://t.me/{bot_info.username}/{config.tg_bot.web_app_name.replace('-', '_')}",
                    )
                ]
            ]
        ),
    )


@web_app_router.message(Command("reply_web_app"))
async def user_reply_web_app(message: Message, config: Config):
    await message.answer(
        "Added reply keyboard button!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Launch!",
                        web_app=WebAppInfo(
                            url=f"{config.web.domain}/{config.tg_bot.web_app_name}"
                        ),
                    )
                ]
            ],
            resize_keyboard=True,
        ),
    )


@web_app_router.message(Command("rm_reply_web_app"))
async def user_rm_reply_web_app(message: Message):
    await message.answer("Reply button removed!", reply_markup=ReplyKeyboardRemove())


@web_app_router.message(F.web_app_data)
async def user_web_app_data(message: Message):
    await message.answer("Got info: <i>" + message.web_app_data.data + "</i>")
