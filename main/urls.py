from django.urls import path

from .views import wechat_main


urlpatterns = [
    path("", wechat_main),
]
