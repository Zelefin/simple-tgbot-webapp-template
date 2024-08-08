import logging
import json
from pathlib import Path
import random
import aiohttp_cors
from aiohttp import web
from aiohttp.web_response import json_response
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request

from infrastructure.api.utils import parse_init_data, validate_telegram_data
from infrastructure.database.repo.requests import RequestsRepo


async def index_handler(request: Request):
    web_app_name = request.app["web_app_name"]
    return FileResponse(
        Path(__file__).parents[2].resolve() / f"frontend/{web_app_name}/dist/index.html"
    )


async def greet_handler(request: Request):
    data = await request.post()
    if not data or not validate_telegram_data(data.get("_auth"), request.app["config"]):
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    session_pool = request.app["session_pool"]
    bot = request.app["bot"]

    telegram_data = parse_init_data(data.get("_auth"))
    user = json.loads(telegram_data.get("user"))

    # Just an example with db usage
    async with session_pool() as session:
        repo = RequestsRepo(session)
        user_fullname = (
            user.get("first_name") + " " + user.get("last_name")
            if user.get("last_name")
            else user.get("first_name")
        )
        user_db = await repo.users.get_or_create_user(
            user.get("id"),
            user_fullname,
            user.get("language_code"),
            user.get("username"),
        )
        logging.info("Handling request from user: %s", user)

    try:
        await bot.send_message(
            chat_id=user_db.user_id,
            text="Thanks!"
            + random.choice(
                ["😊", "🌟", "🍕", "🐧", "🐰", "🐶", "🌺", "🍓", "☀️", "🎉"]
            ),
        )
    except Exception as e:
        logging.error(f"Error sending message: %s", e)
        return json_response({"ok": False})

    return json_response({"ok": True})


def setup_web_app_routes(app: web.Application):
    web_app_name = app["web_app_name"]

    # cors for local development
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*"
            )
        },
    )
    app.router.add_get("", index_handler)
    app.router.add_post("/greet", greet_handler)
    app.router.add_static(
        "/assets/",
        Path(__file__).parents[2].resolve() / f"frontend/{web_app_name}/dist/assets",
    )

    for route in list(app.router.routes()):
        cors.add(route)
