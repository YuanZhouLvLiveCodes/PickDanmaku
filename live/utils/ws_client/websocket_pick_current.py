from aiohttp import WSMsgType, web

from live.utils.ws_client.websocket_broadcast import broadcast, broadcast_text
from live.utils.ws_client.websocket_client import WebSocketClientSet, WebSocketClientDict


# websocket_clients_current: Set[WebSocketResponse] = set()  # WebSocket 客户端列表

class WebSocketPickCurrent(WebSocketClientSet):
    def __init__(self):
        super().__init__()

    # WebSocket 处理函数
    async def handle_current(self, request):
        """处理 WebSocket 连接"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.add_client(ws)
        print("当前消息 WebSocket 客户端已连接")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    print(f"收到前端当前消息：{msg.data}")
                    await broadcast(msg.data, self.websocket_set)
                elif msg.type == WSMsgType.ERROR:
                    print(f"当前消息 WebSocket 错误：{ws.exception()}")
        finally:
            self.remove_client(ws)
            print("当前消息 WebSocket 客户端已断开")

        return ws
