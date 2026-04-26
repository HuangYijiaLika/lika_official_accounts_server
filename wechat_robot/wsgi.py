"""
本文件提供 WSGI 入口（用于同步服务器部署，例如 Gunicorn/uWSGI 等）。
这是 Django 默认生成的部署入口之一。
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wechat_robot.settings")

application = get_wsgi_application()
