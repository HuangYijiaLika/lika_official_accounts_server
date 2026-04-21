"""
本文件定义数据库里的数据模型（表结构）。
这里的 User/Offer 会通过 Django ORM 映射到数据库表，并由迁移文件创建/变更真实表结构。
"""

from django.db import models

from .constants import USER_STATE_DEFAULT


class User(models.Model):
    username = models.CharField(max_length=512, unique=True)
    state = models.IntegerField(default=USER_STATE_DEFAULT)
    request_queue = models.CharField(max_length=1024, default="[]")

    def __str__(self) -> str:
        return f"User({self.username}, state={self.state})"


class Offer(models.Model):
    company = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    position = models.CharField(max_length=64)
    salary = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"Offer({self.company}, {self.city}, {self.position}, {self.salary})"
