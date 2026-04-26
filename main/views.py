"""
本文件是 Django 的视图层（HTTP 请求入口）。
主要职责：接收微信服务器发来的 GET/POST，解析 XML，分发到对应处理逻辑，并返回微信要求格式的 XML 回复。
"""

from pathlib import Path
from xml.etree import ElementTree

import requests
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from main.constants import (
    AUTHORITY_CHECK_PASS,
    HELP_BY_COMMAND,
    MESSAGE_COMMIT_SUCCESS,
    MESSAGE_HELLO,
    MESSAGE_HELP,
    MESSAGE_NO_PERMISSION,
    MESSAGE_NOT_OWNER,
    MESSAGE_OFFER_NOT_FOUND,
    MESSAGE_INIT,
    MESSAGE_UNKNOWN_COMMAND,
    MESSAGE_VALUE_ERROR,
)
from main.lexer import parse_command
from main.services import (
    batch_create_offers,
    check_user_state,
    create_offer,
    create_user,
    delete_all_offers_by_username,
    delete_offer_by_public_id,
    get_user_offer_stats,
    get_user,
    get_offer_by_public_id,
    list_latest_offers,
    list_offers_with_page,
    replace_offer_by_public_id,
    update_offer_by_public_id,
)
from main.wechat_utils import (
    build_image_reply,
    build_text_reply,
    get_access_token,
    wechat_heartbeat,
)


PICS_DIR = Path(__file__).resolve().parent / "pics"


@csrf_exempt
def wechat_main(request: HttpRequest) -> HttpResponse:
    """微信公众号入口：处理 GET 心跳/验证与 POST 消息分发。"""
    try:
        get_access_token()
    except Exception:
        pass

    if request.method == "GET":
        return wechat_heartbeat(request)
    if request.method == "POST":
        return wechat_distributor(request)
    return HttpResponse("Only GET and POST are supported.", status=405)


def wechat_distributor(request: HttpRequest) -> HttpResponse:
    """解析微信 XML，按消息类型（text/image）分发到对应处理函数。"""
    xml_data = ElementTree.fromstring(request.body)
    msg_type = xml_data.findtext("MsgType", default="")
    from_user = xml_data.findtext("FromUserName", default="")
    to_user = xml_data.findtext("ToUserName", default="")

    if msg_type == "text":
        return handle_text_message(xml_data, from_user, to_user)
    if msg_type == "image":
        return handle_image_message(xml_data, from_user, to_user)

    reply = build_text_reply(from_user, to_user, MESSAGE_INIT)
    return HttpResponse(reply, content_type="application/xml")


def handle_text_message(xml_data: ElementTree.Element, from_user: str, to_user: str) -> HttpResponse:
    """处理微信文本消息：解析命令、执行业务逻辑、返回文本回复 XML。"""
    if get_user(from_user) is None:
        create_user(from_user)

    content = xml_data.findtext("Content", default="").strip()
    tokens = parse_command(content)
    message = MESSAGE_UNKNOWN_COMMAND if tokens is None else wechat_command_distributor(from_user, tokens)
    final_message = f"{MESSAGE_HELLO}\n{message}"
    reply = build_text_reply(from_user, to_user, final_message)
    return HttpResponse(reply, content_type="application/xml")


def handle_image_message(xml_data: ElementTree.Element, from_user: str, to_user: str) -> HttpResponse:
    """处理微信图片消息：下载保存图片，并按微信要求返回图片回复 XML。"""
    media_id = xml_data.findtext("MediaId", default="")
    pic_url = xml_data.findtext("PicUrl", default="")

    if not media_id or not pic_url:
        reply = build_text_reply(from_user, to_user, "图片消息缺少必要字段。")
        return HttpResponse(reply, content_type="application/xml")

    PICS_DIR.mkdir(parents=True, exist_ok=True)
    picture_path = PICS_DIR / f"{media_id}.jpg"
    response = requests.get(pic_url, timeout=10)
    picture_path.write_bytes(response.content)

    reply = build_image_reply(from_user, to_user, media_id)
    return HttpResponse(reply, content_type="application/xml")


def wechat_command_distributor(from_user: str, tokens: dict) -> str:
    """按 tokens["command"] 分发到对应业务处理，并返回最终要回复的文本内容。"""
    if check_user_state(from_user, tokens["command"], update=True) != AUTHORITY_CHECK_PASS:
        return MESSAGE_NO_PERMISSION

    command = tokens["command"]
    if command == "value_error":
        return MESSAGE_VALUE_ERROR
    if command == "ping":
        return "pong"
    if command == "help":
        return MESSAGE_HELP
    if command == "help_one":
        target = tokens["target"]
        message = HELP_BY_COMMAND.get(target)
        if message is None:
            return f"未知命令：{target}\n\n{MESSAGE_HELP}"
        return message
    if command == "stats":
        stats = get_user_offer_stats(from_user)
        count = int(stats.get("count") or 0)
        if count == 0:
            return "你还没有提交过 Offer。"
        last_created_at = stats.get("last_created_at")
        last_text = last_created_at.isoformat(sep=" ", timespec="seconds") if last_created_at else ""
        avg_salary = stats.get("avg_salary")
        avg_salary_text = str(int(round(avg_salary))) if avg_salary is not None else ""
        return "\n".join(
            [
                "我的统计：",
                f"count: {count}",
                f"last_created_at: {last_text}",
                f"max_salary: {stats.get('max_salary')}",
                f"min_salary: {stats.get('min_salary')}",
                f"avg_salary: {avg_salary_text}",
            ]
        )
    if command == "my":
        offers, current_page, page_count = list_offers_with_page(
            {"from_user": from_user, "page": tokens.get("page"), "sort-new": True}
        )
        lines = [f"我的 Offer（第 {current_page} / {page_count} 页）", "{"]
        for offer in offers:
            lines.append(f"  {offer}")
        lines.append("}")
        return "\n".join(lines)
    if command == "latest":
        n = tokens.get("n") or 5
        n = min(max(int(n), 1), 20)
        offers = list_latest_offers(n)
        lines = [f"最新 {len(offers)} 条 Offer", "{"]
        for offer in offers:
            lines.append(f"  {offer}")
        lines.append("}")
        return "\n".join(lines)
    if command == "commit":
        public_id = create_offer(tokens, from_user)
        return f"{MESSAGE_COMMIT_SUCCESS}\nID: {public_id}"
    if command == "query":
        return format_query_result(tokens)
    if command == "detail":
        offer = get_offer_by_public_id(tokens["id"])
        if offer is None:
            return MESSAGE_OFFER_NOT_FOUND
        return _format_offer_detail("详情：", offer, include_meta=False)
    if command == "group-commit":
        public_ids = batch_create_offers(tokens["offers"], from_user)
        lines = ["收到啦，这些 Offer 已经保存。", "IDs:"]
        lines.extend(public_ids)
        return "\n".join(lines)
    if command == "edit_update":
        result = update_offer_by_public_id(tokens["id"], from_user, tokens["updates"])
        if result is None:
            return MESSAGE_OFFER_NOT_FOUND
        if result is False:
            return MESSAGE_NOT_OWNER
        return _format_offer_detail("编辑成功：", result, include_meta=False)
    if command == "edit_replace":
        result = replace_offer_by_public_id(
            tokens["id"], from_user, tokens["company"], tokens["city"], tokens["position"], tokens["salary"]
        )
        if result is None:
            return MESSAGE_OFFER_NOT_FOUND
        if result is False:
            return MESSAGE_NOT_OWNER
        return _format_offer_detail("编辑成功：", result, include_meta=False)
    if command == "delete_one":
        result = delete_offer_by_public_id(tokens["id"], from_user)
        if result is None:
            return MESSAGE_OFFER_NOT_FOUND
        if result is False:
            return MESSAGE_NOT_OWNER
        return f"删除成功。\nID: {tokens['id']}"
    if command == "delete_all":
        count = delete_all_offers_by_username(from_user)
        return f"已删除你提交的 Offer：{count} 条"
    return MESSAGE_UNKNOWN_COMMAND


def _format_offer_detail(title: str, offer, include_meta: bool = True) -> str:
    """把 Offer 格式化为多行可读文本（用于 query/edit 的详情输出）。"""
    lines = [
        title,
        f"ID: {offer.public_id}",
        f"company: {offer.company}",
        f"city: {offer.city}",
        f"position: {offer.position}",
        f"salary: {offer.salary}",
    ]
    if include_meta:
        created_at = offer.created_at.isoformat(sep=" ", timespec="seconds")
        username = offer.from_user.username if offer.from_user else ""
        lines.append(f"created_at: {created_at}")
        lines.append(f"from_user: {username}")
    return "\n".join(lines)


def format_query_result(tokens: dict) -> str:
    """格式化查询结果：返回分页列表。"""
    offers, current_page, page_count = list_offers_with_page(tokens)
    if not offers:
        return MESSAGE_OFFER_NOT_FOUND
    lines = [f"第 {current_page} / {page_count} 页", "{"]
    for offer in offers:
        lines.append(f"  {offer}")
    lines.append("}")
    return "\n".join(lines)
