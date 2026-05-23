## main.py
"""ReplyTag - 回复时间标签插件
记录用户每次回复的时间差，打标签供人格感知：
  ≤30秒  → 秒回 💨
  30秒~10分钟 → 正常回复 🤔
  >10分钟 → 回复得慢 😤
"""

import time
from collections import defaultdict

from astrbot.api.event import filter
from astrbot.api.star import Context, Star
from astrbot.core.message.components import Plain
from astrbot.core.platform.astr_message_event import AstrMessageEvent


class ReplyTagPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # { uid: 上次bot回复该用户的时间戳 }
        self._last_reply: dict[str, float] = {}

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        uid = event.get_sender_id()
        bid = event.get_self_id()
        if uid == bid:
            return

        now = time.time()
        prev = self._last_reply.get(uid)

        if prev is not None:
            delta = now - prev  # 秒
            if delta <= 30:
                tag = f"秒回💨"
                detail = f"{int(delta)}秒"
            elif delta <= 600:  # 10分钟
                tag = f"正常回复🤔"
                detail = f"{int(delta//60)}分{int(delta%60)}秒"
            else:
                tag = f"回复得慢😤"
                detail = f"{int(delta//60)}分钟"
        else:
            tag = "初次对话👋"
            detail = ""

        # 写入 extra 供人格读取
        event.set_extra("replytag_label", tag)
        event.set_extra("replytag_delta", detail)
        event.set_extra("replytag_seconds", int(now - prev) if prev else 0)

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        uid = event.get_sender_id()
        if uid:
            self._last_reply[uid] = time.time()
