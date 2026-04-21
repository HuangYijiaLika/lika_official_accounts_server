"""
本文件是项目级 URL 路由入口。
它把 /wechat/ 转发给 main 应用的路由，并保留 /admin/ 后台入口。
"""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("wechat/", include("main.urls")),
]
