from dataclasses import dataclass

from live.model.bilibili.bili_message import BiliMessage


@dataclass
class BiliGift(BiliMessage):
    """
    data = {
            "type": "gift",
            "room_id": client.room_id,
            "uname": message.uname,
            "gift_name": message.gift_name,
            "num": message.num
        }
    """
    type: str = "gift"
    gift_name: str = None
    num: int = None
