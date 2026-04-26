"""
本文件提供与 Offer 相关的业务函数。
包括：创建/批量创建 Offer、按条件过滤查询、以及分页与排序（按时间/按薪资）。
"""

import math
import zlib

from django.db.models import Avg, Count, Max, Min, Q, QuerySet

from main.constants import RECORDS_PER_PAGE, RETURN_STATE_SUCCESS
from main.models import Offer
from main.services.user_services import get_user


FILTER_FIELDS = ("company", "city", "position")


def _compute_public_id(base: str) -> str:
    """对 base 字符串计算 CRC32，并返回固定 8 位十六进制字符串。"""
    value = zlib.crc32(base.encode("utf-8")) & 0xFFFFFFFF
    return format(value, "08x")


def generate_offer_public_id(offer: Offer, username: str) -> str:
    """为 offer 生成 public_id；如发生碰撞则追加 #n 后缀重算直到唯一。"""
    created_at = offer.created_at.isoformat()
    # public_id 的输入串：6 个字段按约定顺序，用 | 连接
    base = f"{offer.company}|{offer.city}|{offer.position}|{offer.salary}|{created_at}|{username}"

    candidate = _compute_public_id(base)
    if not Offer.objects.filter(public_id=candidate).exists():
        return candidate

    # CRC32 可能碰撞：发现已存在时，追加 #n 后缀并重算，直到找到未占用的值
    suffix = 1
    while True:
        candidate = _compute_public_id(f"{base}#{suffix}")
        if not Offer.objects.filter(public_id=candidate).exists():
            return candidate
        suffix += 1


def create_offer(data: dict, username: str) -> str:
    """创建一条 Offer，并返回其 public_id。"""
    user = get_user(username)
    offer = Offer.objects.create(
        company=data["company"],
        city=data["city"],
        position=data["position"],
        salary=data["salary"],
        from_user=user,
    )
    offer.public_id = generate_offer_public_id(offer, username)
    offer.save(update_fields=["public_id"])
    return offer.public_id


def batch_create_offers(items: list[dict], username: str) -> list[str]:
    """批量创建 Offer，按输入顺序返回每条的 public_id 列表。"""
    user = get_user(username)
    public_ids: list[str] = []
    for item in items:
        offer = Offer.objects.create(
            company=item["company"],
            city=item["city"],
            position=item["position"],
            salary=item["salary"],
            from_user=user,
        )
        offer.public_id = generate_offer_public_id(offer, username)
        offer.save(update_fields=["public_id"])
        public_ids.append(offer.public_id)
    return public_ids


def get_offer_by_public_id(public_id: str) -> Offer | None:
    """按 public_id 查询 Offer（不区分大小写）；找不到返回 None。"""
    value = public_id.strip().lower()
    if not value:
        return None
    return Offer.objects.filter(public_id=value).first()


def _check_offer_owner(offer: Offer, username: str) -> bool:
    """判断 offer 的 from_user 是否为 username（用于权限校验）。"""
    if offer.from_user is None:
        return False
    return offer.from_user.username == username


def update_offer_by_public_id(public_id: str, username: str, updates: dict) -> Offer | bool | None:
    """按 public_id 更新指定字段；返回 Offer / False(无权限) / None(未找到)。"""
    offer = get_offer_by_public_id(public_id)
    if offer is None:
        return None
    if not _check_offer_owner(offer, username):
        return False

    update_fields: list[str] = []
    for field in ("company", "city", "position", "salary"):
        if field in updates:
            setattr(offer, field, updates[field])
            update_fields.append(field)

    if not update_fields:
        return offer

    offer.save(update_fields=update_fields)
    return offer


def replace_offer_by_public_id(
    public_id: str, username: str, company: str, city: str, position: str, salary: int
) -> Offer | bool | None:
    """按 public_id 整体替换四个字段；返回 Offer / False(无权限) / None(未找到)。"""
    offer = get_offer_by_public_id(public_id)
    if offer is None:
        return None
    if not _check_offer_owner(offer, username):
        return False

    offer.company = company
    offer.city = city
    offer.position = position
    offer.salary = salary
    offer.save(update_fields=["company", "city", "position", "salary"])
    return offer


def delete_offer_by_public_id(public_id: str, username: str) -> bool | None:
    """按 public_id 删除 Offer；返回 True(成功)/False(无权限)/None(未找到)。"""
    offer = get_offer_by_public_id(public_id)
    if offer is None:
        return None
    if not _check_offer_owner(offer, username):
        return False
    offer.delete()
    return True


def delete_all_offers_by_username(username: str) -> int:
    """删除 username 创建的全部 Offer，返回删除条数。"""
    return Offer.objects.filter(from_user__username=username).delete()[0]


def list_latest_offers(n: int) -> QuerySet[Offer]:
    """按 created_at 倒序返回最新 n 条 Offer。"""
    return Offer.objects.order_by("-created_at")[:n]


def get_user_offer_stats(username: str) -> dict:
    """统计 username 提交的 Offer：数量、最近提交时间、最高/最低/平均薪资。"""
    result = Offer.objects.filter(from_user__username=username).aggregate(
        count=Count("id"),
        last_created_at=Max("created_at"),
        max_salary=Max("salary"),
        min_salary=Min("salary"),
        avg_salary=Avg("salary"),
    )
    return result


def list_offers(filters: dict) -> QuerySet[Offer]:
    """按 filters 过滤并排序 Offer（不分页）。"""
    query = Q()
    for field in FILTER_FIELDS:
        value = filters.get(field)
        if value is not None:
            query &= Q(**{field: value})

    from_user = filters.get("from_user")
    if from_user is not None:
        query &= Q(from_user__username=from_user)

    results = Offer.objects.filter(query)
    if filters.get("sort-new"):
        results = results.order_by("-created_at")
    if filters.get("sort-salary"):
        results = results.order_by("-salary")
    return results


def list_offers_with_page(filters: dict) -> tuple[QuerySet[Offer], int, int]:
    """按 filters 查询 Offer 并分页，返回（当前页结果、当前页、总页数）。"""
    results = list_offers(filters)
    total = results.count()
    page_count = max(1, math.ceil(total / RECORDS_PER_PAGE))

    requested_page = filters.get("page")
    if requested_page is None:
        current_page = 1
    else:
        current_page = min(max(int(requested_page), 1), page_count)

    start = (current_page - 1) * RECORDS_PER_PAGE
    end = start + RECORDS_PER_PAGE
    return results[start:end], current_page, page_count
