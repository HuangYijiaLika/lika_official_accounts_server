"""
本文件提供与“微信接口”相关的工具函数。
包括：组装微信要求的 XML 回复（文本/图片）、GET 心跳/验证辅助、以及 access_token 的获取与缓存。
"""

import time
from xml.sax.saxutils import escape

import requests
from django.conf import settings
from django.http import HttpRequest, HttpResponse


access_token = ""
expire_time = 0.0


def build_text_reply(to_user: str, from_user: str, content: str) -> str:
    safe_content = escape(content)
    return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{safe_content}]]></Content>
</xml>"""


def build_image_reply(to_user: str, from_user: str, media_id: str) -> str:
    return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[{media_id}]]></MediaId>
</Image>
</xml>"""


def wechat_heartbeat(request: HttpRequest) -> HttpResponse:
    echostr = request.GET.get("echostr")
    if echostr:
        return HttpResponse(echostr)
    return HttpResponse("wechat server is running")


def get_access_token() -> str:
    global access_token, expire_time

    app_id = settings.WECHAT_APP_ID
    app_secret = settings.WECHAT_APP_SECRET
    if not app_id or not app_secret:
        return ""

    if time.time() <= expire_time and access_token:
        return access_token

    url = "https://api.weixin.qq.com/cgi-bin/token"
    response = requests.get(
        url,
        params={
            "grant_type": "client_credential",
            "appid": app_id,
            "secret": app_secret,
        },
        timeout=10,
    )
    data = response.json()
    if "access_token" not in data:
        raise ValueError(f"Failed to get access token: {data}")

    access_token = data["access_token"]
    expire_time = time.time() + int(data["expires_in"])
    return access_token
