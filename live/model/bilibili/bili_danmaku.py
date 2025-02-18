from dataclasses import dataclass

from live.model.bilibili.bili_message import BiliMessage


@dataclass
class BiliDanmaku(BiliMessage):
    """
        data = {
            "type": "danmaku",
            "room_id": client.room_id,
            "uname": message.uname,
            "msg": message.msg
        }
    """
    msg: str = None
    type: str = "danmaku"
