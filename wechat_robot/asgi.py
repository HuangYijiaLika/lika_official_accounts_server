"""
本文件提供 ASGI 入口（用于异步服务器部署，例如 Uvicorn/Daphne）。
教学版通常用不到，但这是 Django 默认生成的部署入口之一。
"""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wechat_robot.settings")

application = get_asgi_application()
