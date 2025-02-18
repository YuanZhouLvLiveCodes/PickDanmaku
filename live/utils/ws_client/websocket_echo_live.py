import json

from aiohttp import WSMsgType, web

from live.utils.ws_client.websocket_broadcast import broadcast, broadcast_text
from live.utils.ws_client.websocket_client import WebSocketClientSet, WebSocketClientDict


# websocket_clients_type_echo: Dict[str, WebSocketResponse] = dict()  # WebSocket 客户端列表

class WebSocketEchoLive(WebSocketClientDict):
    def __init__(self):
        super().__init__()
    # WebSocket 处理函数
    async def handle_type_echo(self, request):
        """处理 WebSocket 连接"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        print("当前消息 WebSocket 客户端已连接")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"收到前端当前消息：{data}")
                    from_uuid = data["from"]["uuid"]
                    print(from_uuid)
                    if data["action"] in ["ping"]:
                        self.add_client(ws, from_uuid)
                    elif data["action"] in ["hello"]:
                        print("hello from: " + from_uuid)
                        pass
                    else:
                        await broadcast_text(msg.data, self.websocket_dict)

                elif msg.type == WSMsgType.ERROR:
                    print(f"当前消息 WebSocket 错误：{ws.exception()}")
        finally:
            self.remove_client(ws)
            print("当前消息 WebSocket 客户端已断开")

        return ws
