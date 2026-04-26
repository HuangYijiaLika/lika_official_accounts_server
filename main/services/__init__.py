"""
本包汇总 services 层对外提供的函数，方便在 views 中统一导入。
这里的函数负责“业务逻辑”（创建/查询 Offer、用户状态检查等），避免把业务细节写进 views。
"""

from .offer_services import (
    batch_create_offers,
    create_offer,
    delete_all_offers_by_username,
    delete_offer_by_public_id,
    get_offer_by_public_id,
    list_offers,
    list_offers_with_page,
    replace_offer_by_public_id,
    update_offer_by_public_id,
)
from .user_services import (
    check_user_state,
    create_user,
    get_user,
    get_user_state,
    reset_user_state,
    update_user_state,
)

__all__ = [
    "batch_create_offers",
    "check_user_state",
    "create_offer",
    "create_user",
    "delete_all_offers_by_username",
    "delete_offer_by_public_id",
    "get_user",
    "get_user_state",
    "get_offer_by_public_id",
    "list_offers",
    "list_offers_with_page",
    "replace_offer_by_public_id",
    "reset_user_state",
    "update_offer_by_public_id",
    "update_user_state",
]
