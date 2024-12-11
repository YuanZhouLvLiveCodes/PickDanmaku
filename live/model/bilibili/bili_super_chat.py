from dataclasses import dataclass

from live.api.bilibili.model import BiliMessage


@dataclass
class BiliSuperChat(BiliMessage):
    """
    data = {
            "type": "superchat",
            "room_id": client.room_id,
            "uname": message.uname,
            "price": message.price,
            "msg": message.message
        }
    """
    type: str = "superchat"
    price: int = None
    msg: str = None