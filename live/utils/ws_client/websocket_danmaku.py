from aiohttp import WSMsgType, web

from live.utils.ws_client.websocket_broadcast import broadcast, broadcast_text
from live.utils.ws_client.websocket_client import WebSocketClientSet, WebSocketClientDict


class WebSocketDanmaku(WebSocketClientSet):
    def __init__(self):
        super().__init__()
    async def handle_websocket(self, request):
        """处理 WebSocket 连接"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.add_client(ws)
        print("WebSocket 客户端已连接")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    print(f"收到前端消息：{msg.data}")
                    await broadcast(msg.data, self.websocket_set)
                elif msg.type == WSMsgType.ERROR:
                    print(f"WebSocket 错误：{ws.exception()}")
        finally:
            self.remove_client(ws)
            print("WebSocket 客户端已断开")

        return ws
