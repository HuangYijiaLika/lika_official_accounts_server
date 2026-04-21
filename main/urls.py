"""
本文件定义 main 应用对外暴露的 URL 路由。
这里把 /wechat/（在项目级 urls.py 中 include 进来）映射到 wechat_main 视图函数。
"""

from django.urls import path

from .views import wechat_main


urlpatterns = [
    path("", wechat_main),
]
