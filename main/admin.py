"""
本文件用于配置 Django Admin 后台。
把 User/Offer 模型注册到后台后，就能在 /admin/ 页面里可视化查看与管理数据。
"""

from django.contrib import admin

from .models import Offer, User


admin.site.register(User)
admin.site.register(Offer)
