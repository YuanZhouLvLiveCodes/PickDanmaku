from dataclasses import dataclass

from live.model.bilibili.bili_message import BiliMessage


@dataclass
class BiliBuyGuard(BiliMessage):
    """
        data = {
            "room_id": client.room_id,
            "uname": message.username,
            "guard_level": message.guard_level,
            "num": message.num,
            "price": message.price,
            "uid": message.uid,
            "platform": "bilibili",
            "room_title": room_info["room_title"],
            "room_uid": room_info["room_uid"],
            "room_uname": room_info["room_uname"],
        }
    """
    type: str = "buy_guard"
    guard_level: int = None
    num: int = None
    price: int = None
