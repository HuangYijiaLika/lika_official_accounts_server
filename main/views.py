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
    MESSAGE_COMMIT_SUCCESS,
    MESSAGE_HELLO,
    MESSAGE_HELP,
    MESSAGE_NO_PERMISSION,
    MESSAGE_ONLY_TEXT_OR_IMAGE,
    MESSAGE_UNKNOWN_COMMAND,
)
from main.lexer import parse_command
from main.services import (
    batch_create_offers,
    check_user_state,
    create_offer,
    create_user,
    get_user,
    list_offers_with_page,
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
    xml_data = ElementTree.fromstring(request.body)
    msg_type = xml_data.findtext("MsgType", default="")
    from_user = xml_data.findtext("FromUserName", default="")
    to_user = xml_data.findtext("ToUserName", default="")

    if msg_type == "text":
        return handle_text_message(xml_data, from_user, to_user)
    if msg_type == "image":
        return handle_image_message(xml_data, from_user, to_user)

    reply = build_text_reply(from_user, to_user, MESSAGE_ONLY_TEXT_OR_IMAGE)
    return HttpResponse(reply, content_type="application/xml")


def handle_text_message(xml_data: ElementTree.Element, from_user: str, to_user: str) -> HttpResponse:
    if get_user(from_user) is None:
        create_user(from_user)

    content = xml_data.findtext("Content", default="").strip()
    tokens = parse_command(content)
    message = MESSAGE_UNKNOWN_COMMAND if tokens is None else wechat_command_distributor(from_user, tokens)
    final_message = f"{MESSAGE_HELLO}\n{message}"
    reply = build_text_reply(from_user, to_user, final_message)
    return HttpResponse(reply, content_type="application/xml")


def handle_image_message(xml_data: ElementTree.Element, from_user: str, to_user: str) -> HttpResponse:
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
    if check_user_state(from_user, tokens["command"], update=True) != AUTHORITY_CHECK_PASS:
        return MESSAGE_NO_PERMISSION

    command = tokens["command"]
    if command == "help":
        return MESSAGE_HELP
    if command == "commit":
        create_offer(tokens, from_user)
        return MESSAGE_COMMIT_SUCCESS
    if command == "query":
        return format_query_result(tokens)
    if command == "group-commit":
        batch_create_offers(tokens["offers"], from_user)
        return MESSAGE_COMMIT_SUCCESS
    return MESSAGE_UNKNOWN_COMMAND


def format_query_result(tokens: dict) -> str:
    offers, current_page, page_count = list_offers_with_page(tokens)
    lines = [f"第 {current_page} / {page_count} 页", "{"]
    for offer in offers:
        lines.append(f"  {offer}")
    lines.append("}")
    return "\n".join(lines)
