"""Import all routers and add them to routers_list."""

from .admin import admin_router
from .user import user_router
from .simple_web_app import simple_web_app_router

routers_list = [
    admin_router,
    user_router,
    simple_web_app_router,
]

__all__ = [
    "routers_list",
]
