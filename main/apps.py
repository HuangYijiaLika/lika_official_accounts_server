"""
本文件是 main 应用的 Django App 配置。
一般不需要改；Django 会通过它识别应用名称、默认主键类型等基础配置。
"""

from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"
