"""
本文件提供与 User 相关的业务函数。
包括：创建/查询用户、读取/更新用户状态位、以及基于时间窗口的简单高频请求检测。
"""

import json
import time

from main.constants import (
    AUTHORITY_CHECK_FAILED,
    AUTHORITY_CHECK_PASS,
    AUTHORITY_CHECK_USER_NOT_EXIST,
    REQUEST_QUEUE_LIMIT_SIZE,
    REQUEST_QUEUE_LIMIT_TIME,
    RETURN_STATE_SUCCESS,
    USER_STATE_BANNED,
    USER_STATE_DEFAULT,
    USER_STATE_SPIDER,
)
from main.models import User


def get_user(username: str) -> User | None:
    """按 username 查询用户；不存在返回 None。"""
    return User.objects.filter(username=username).first()


def create_user(username: str) -> User:
    """创建并返回一个新用户。"""
    return User.objects.create(username=username)


def get_user_state(username: str) -> int | None:
    """获取用户 state；用户不存在返回 None。"""
    user = get_user(username)
    if user is None:
        return None
    return user.state


def reset_user_state(username: str) -> int:
    """重置用户状态与请求队列（用户不存在也视为成功）。"""
    user = get_user(username)
    if user is None:
        return RETURN_STATE_SUCCESS
    user.state = USER_STATE_DEFAULT
    user.request_queue = "[]"
    user.save()
    return RETURN_STATE_SUCCESS


def update_user_state(username: str, state: int) -> int:
    """设置用户 state（不存在则先创建）。"""
    user = get_user(username)
    if user is None:
        user = create_user(username)
    user.state = state
    user.save()
    return RETURN_STATE_SUCCESS


def _load_request_queue(user: User) -> list[int]:
    """从 user.request_queue 解析最近请求时间戳列表；异常时返回空列表。"""
    try:
        queue = json.loads(user.request_queue)
    except json.JSONDecodeError:
        return []
    if isinstance(queue, list):
        return [int(item) for item in queue]
    return []


def _save_request_queue(user: User, queue: list[int]) -> None:
    """把请求时间戳列表写回 user.request_queue 并保存。"""
    user.request_queue = json.dumps(queue)
    user.save()


def check_user_state(username: str, command: str, update: bool = False) -> int:
    """检查用户是否可继续使用；可选更新高频请求队列并触发封禁标记。"""
    del command

    user = get_user(username)
    if user is None:
        if not update:
            return AUTHORITY_CHECK_USER_NOT_EXIST
        user = create_user(username)

    if update:
        queue = _load_request_queue(user)
        current_time = int(time.time())

        while queue and current_time - queue[0] >= REQUEST_QUEUE_LIMIT_TIME:
            queue.pop(0)

        queue.append(current_time)
        if len(queue) >= REQUEST_QUEUE_LIMIT_SIZE:
            user.state |= USER_STATE_SPIDER

        _save_request_queue(user, queue)

    if user.state & USER_STATE_BANNED:
        return AUTHORITY_CHECK_FAILED
    if user.state & USER_STATE_SPIDER:
        return AUTHORITY_CHECK_FAILED
    return AUTHORITY_CHECK_PASS
