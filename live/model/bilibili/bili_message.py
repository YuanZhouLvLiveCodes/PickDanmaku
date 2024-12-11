import json
from dataclasses import dataclass, asdict

from live.api import PLATFORM_NAME


@dataclass
class BiliMessage:
    """
        data = {
            "type": "danmaku",
            "room_id": client.room_id,
            "uname": message.uname,
            "msg": message.msg
        }
    """
    type: str = None
    room_id: int = None
    uname: str = None
    uid: str = None
    platform: str = "bilibili"
    room_title: str = None
    room_uid: str = None
    room_uname: str = None
    msg: str = None
    data: dict = None
    message: str = None

    def __str__(self):
        data = asdict(self)
        if "platform" in data:
            data["platform_name"] = PLATFORM_NAME[data["platform"]]
        return json.dumps(data, ensure_ascii=False)
