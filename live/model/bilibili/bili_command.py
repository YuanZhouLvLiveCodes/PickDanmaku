from dataclasses import dataclass

from live.model.bilibili.bili_message import BiliMessage


@dataclass
class BiliCommand(BiliMessage):
    type: str = "command"
    room_id: int = None
    original_data: dict = None
    cmd: str = None
