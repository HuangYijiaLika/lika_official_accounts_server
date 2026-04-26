"""
本文件提供与“微信接口”相关的工具函数。
包括：组装微信要求的 XML 回复（文本/图片）、GET 心跳/验证辅助、以及 access_token 的获取与缓存。
"""

import hashlib
import time

import requests
from django.conf import settings
from django.http import HttpRequest, HttpResponse


access_token = ""
expire_time = 0.0


def build_text_reply(to_user: str, from_user: str, content: str) -> str:
    """生成微信 text 类型回复的 XML 字符串。"""
    safe_content = content.replace("]]>", "]]]]><![CDATA[>")
    return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{safe_content}]]></Content>
</xml>"""


def build_image_reply(to_user: str, from_user: str, media_id: str) -> str:
    """生成微信 image 类型回复的 XML 字符串。"""
    return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[{media_id}]]></MediaId>
</Image>
</xml>"""


def _check_wechat_signature(signature: str, timestamp: str, nonce: str) -> bool:
    """按微信文档规则校验签名：sha1(sort([token,timestamp,nonce]).join())."""
    token = settings.WECHAT_TOKEN
    parts = [token, timestamp, nonce]
    parts.sort()
    raw = "".join(parts).encode("utf-8")
    digest = hashlib.sha1(raw).hexdigest()
    return digest == signature


def wechat_heartbeat(request: HttpRequest) -> HttpResponse:
    """处理微信服务器 GET 验证：有 echostr 返回 echostr，否则返回运行提示。"""
    echostr = request.GET.get("echostr")
    if echostr:
        signature = request.GET.get("signature", "")
        timestamp = request.GET.get("timestamp", "")
        nonce = request.GET.get("nonce", "")
        if signature and timestamp and nonce and _check_wechat_signature(signature, timestamp, nonce):
            return HttpResponse(echostr)
        return HttpResponse("invalid signature", status=403)
    return HttpResponse("wechat server is running")


def get_access_token() -> str:
    """获取并缓存微信 access_token；未配置 appid/secret 时返回空字符串。"""
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
