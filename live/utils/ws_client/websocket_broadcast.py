import asyncio
import json
from typing import Dict, Set

from aiohttp.web_ws import WebSocketResponse

from live.model.bilibili.bili_message import BiliMessage


async def broadcast(message: BiliMessage, websocket_clients: Set[WebSocketResponse]):
    """向所有 WebSocket 客户端广播消息"""
    if websocket_clients:
        payload = str(message)
        # print("开始广播", payload)
        result = await asyncio.gather(*[ws.send_str(payload) for ws in websocket_clients])
        # print("广播结果", websocket_clients, result)


async def broadcast_text(payload: str, websocket_clients: Dict[str, WebSocketResponse]):
    """向所有 WebSocket 客户端广播消息"""
    if websocket_clients:
        payload_json = json.loads(payload)
        rather_than_uuid = payload_json["from"]["name"]
        # payload = json.dumps(str(message))
        print("开始广播" + str(payload))
        result = await asyncio.gather(
            *[ws.send_str(payload) for uuid, ws in websocket_clients.items() if uuid != rather_than_uuid])
        # print("广播结果", websocket_clients, result)
