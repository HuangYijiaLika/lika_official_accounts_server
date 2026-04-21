"""
本文件提供与 Offer 相关的业务函数。
包括：创建/批量创建 Offer、按条件过滤查询、以及分页与排序（按时间/按薪资）。
"""

import math

from django.db.models import Q, QuerySet

from main.constants import RECORDS_PER_PAGE, RETURN_STATE_SUCCESS
from main.models import Offer
from main.services.user_services import get_user


FILTER_FIELDS = ("company", "city", "position")


def create_offer(data: dict, username: str) -> int:
    user = get_user(username)
    Offer.objects.create(
        company=data["company"],
        city=data["city"],
        position=data["position"],
        salary=data["salary"],
        from_user=user,
    )
    return RETURN_STATE_SUCCESS


def batch_create_offers(items: list[dict], username: str) -> int:
    user = get_user(username)
    offers = [
        Offer(
            company=item["company"],
            city=item["city"],
            position=item["position"],
            salary=item["salary"],
            from_user=user,
        )
        for item in items
    ]
    Offer.objects.bulk_create(offers)
    return RETURN_STATE_SUCCESS


def list_offers(filters: dict) -> QuerySet[Offer]:
    query = Q()
    for field in FILTER_FIELDS:
        value = filters.get(field)
        if value is not None:
            query &= Q(**{field: value})

    results = Offer.objects.filter(query)
    if filters.get("sort-new"):
        results = results.order_by("-created_at")
    if filters.get("sort-salary"):
        results = results.order_by("-salary")
    return results


def list_offers_with_page(filters: dict) -> tuple[QuerySet[Offer], int, int]:
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
