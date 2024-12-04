import json
import os
import asyncio
from aiohttp import web, WSMsgType
import random
from typing import Optional, Set

import aiohttp
import blivedm
from aiohttp.web_ws import WebSocketResponse

import blivedm.models.web as web_models
import blivedm.models.open_live as open_live_models

# 配置项
TEST_ROOM_IDS = [
    8487238,
    # 32736947,
    # 23557863,
    # 755663,
    # 21652717,
    # 1736192992,
]  # 替换为你的直播间ID列表
SESSDATA = ''
# 全局变量
session: Optional[aiohttp.ClientSession] = None  # HTTP 会话
websocket_clients_danmaku: Set[WebSocketResponse] = set()  # WebSocket 客户端列表
websocket_clients_current: Set[WebSocketResponse] = set()  # WebSocket 客户端列表

HTTP_HOST = 'mc.mineserv.cn'
HTTP_PORT = 8081
HTTP_SCHEME = 'http'

from dataclasses import dataclass, asdict


@dataclass
class Info:
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

    def __str__(self):
        return json.dumps(asdict(self), ensure_ascii=False)


@dataclass
class Danmaku(Info):
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


@dataclass
class Gift(Info):
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



# 初始化 HTTP 会话
def init_session() -> aiohttp.ClientSession:
    cookies = aiohttp.CookieJar()
    cookies.update_cookies({'SESSDATA': SESSDATA})
    session = aiohttp.ClientSession(cookie_jar=cookies)
    return session


# 主程序
async def main():
    global session
    session = init_session()

    # 启动 Web 服务
    app = web.Application()
    app.add_routes([
        # 提供 index.html 页面
        web.get('/', handle_index),
        # 提供 display.html 页面
        web.get('/display', handle_display),
        # 提供 WebSocket 服务
        web.get('/ws', handle_websocket),
        # 提供 WebSocket 服务
        web.get('/currentWs', handle_current),
        # 处理静态资源请求
        web.get("/face/{uid}", handle_face),
        web.get("/assets/{file_name}", handle_assets)
    ])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HTTP_HOST, HTTP_PORT)  # 在 localhost:8081 启动
    await site.start()
    print(f"Web server started at {HTTP_SCHEME}://{HTTP_HOST}:{str(HTTP_PORT)}")

    # 启动弹幕监听
    try:
        await run_blive_clients()
    finally:
        await session.close()


async def handle_assets(request):
    """处理静态资源请求"""
    asset_path = str(os.path.join(os.path.dirname(__file__), 'assets', request.match_info['file_name']))
    return web.FileResponse(asset_path)


async def downloadFile(fase_url, fase_path):
    try:
        async with session.get(fase_url) as response:
            with open(fase_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
        return True
    except Exception as e:
        print(e)
        return False


async def handle_face(request):
    """处理头像资源请求"""
    uid = request.match_info['uid']
    if not uid or not uid.isdigit():
        uid = "noface"
    parent_path = os.path.join(os.path.dirname(__file__), 'assets', "face")
    if not os.path.exists(parent_path):
        os.mkdir(parent_path)
    fase_path = str(os.path.join(os.path.dirname(__file__), 'assets', "face", uid))
    if uid == "noface":
        return web.Response(status=200, body=open(fase_path, 'rb').read(), content_type="image/jpeg")
    if not os.path.exists(fase_path):
        print("下载头像")
        data = await session.get(f"https://api.bilibili.com/x/space/app/index?mid={uid}",
                                 headers={
                                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                                     "Referer": "https://space.bilibili.com/" + uid + "/dynamic"
                                 })
        data_json = await data.json()
        if data_json['code'] == 0:
            fase_url = data_json['data']["info"]['face']
            result = await downloadFile(fase_url, fase_path)
            if result:
                return web.Response(status=200, body=open(fase_path, 'rb').read(), content_type=data.content_type)
    else:
        return web.Response(status=200, body=open(fase_path, 'rb').read(), content_type="image/jpeg")


# 提供 index.html
async def handle_index(request):
    """提供 index.html 页面"""
    index_path = os.path.join(os.path.dirname(__file__), 'index.html')
    return web.FileResponse(index_path)


# 提供 display.html
async def handle_display(request):
    """提供 display.html 页面"""
    display_path = os.path.join(os.path.dirname(__file__), 'display.html')
    return web.FileResponse(display_path)


# WebSocket 处理函数
async def handle_websocket(request):
    """处理 WebSocket 连接"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    websocket_clients_danmaku.add(ws)
    print("WebSocket 客户端已连接")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                print(f"收到前端消息：{msg.data}")
                await broadcast(msg.data, websocket_clients_danmaku)
            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket 错误：{ws.exception()}")
    finally:
        websocket_clients_danmaku.remove(ws)
        print("WebSocket 客户端已断开")

    return ws


# WebSocket 处理函数
async def handle_current(request):
    """处理 WebSocket 连接"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    websocket_clients_current.add(ws)
    print("当前消息 WebSocket 客户端已连接")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                print(f"收到前端当前消息：{msg.data}")
                await broadcast(msg.data, websocket_clients_current)
            elif msg.type == WSMsgType.ERROR:
                print(f"当前消息 WebSocket 错误：{ws.exception()}")
    finally:
        websocket_clients_current.remove(ws)
        print("当前消息 WebSocket 客户端已断开")

    return ws


# 运行多个 B站直播间的弹幕监听
async def run_blive_clients():
    danmaku_clients = [blivedm.BLiveClient(room_id, session=session) for room_id in TEST_ROOM_IDS]
    danmaku_handler = DanmakuHandler()
    # current_handler = CurrentHandler()

    for client in danmaku_clients:
        client.set_handler(danmaku_handler)
        client.start()

    try:
        await asyncio.gather(*[client.join() for client in danmaku_clients])
    finally:
        await asyncio.gather(*[client.stop_and_close() for client in danmaku_clients])


# 自定义弹幕处理器
class DanmakuHandler(blivedm.BaseHandler):
    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        # 调度异步任务
        asyncio.create_task(self.handle_danmaku(client, message))

    async def handle_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        """处理弹幕事件并广播给 WebSocket 客户端"""
        data: Danmaku = Danmaku(**{
            "room_id": client.room_id,
            "uname": message.uname,
            "msg": message.msg,
            "uid": message.uid
        })
        print(f'[弹幕] {data}')
        await broadcast(data, websocket_clients_danmaku)

    def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        # 调度异步任务
        asyncio.create_task(self.handle_gift(client, message))

    async def handle_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        """处理礼物事件并广播给 WebSocket 客户端"""
        data: Gift = Gift(**{
            "room_id": client.room_id,
            "uname": message.uname,
            "gift_name": message.gift_name,
            "num": message.num,
            "uid": message.uid
        })
        print(f'[礼物] {data}')
        await broadcast(data, websocket_clients_danmaku)

# 自定义弹幕处理器
# class CurrentHandler(blivedm.BaseHandler):
#     def _on_change_current(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
#         # 调度异步任务
#         asyncio.create_task(self.handle_danmaku(client, message))
#
#     async def handle_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
#         """处理弹幕事件并广播给 WebSocket 客户端"""
#         data: Danmaku = Danmaku(**{
#             "room_id": client.room_id,
#             "uname": message.uname,
#             "msg": message.msg,
#             "uid": message.uid
#         })
#         # print(f'[弹幕] {data}')
#         await broadcast(data, websocket_clients_current)
#
#     def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
#         # 调度异步任务
#         asyncio.create_task(self.handle_gift(client, message))
#
#     async def handle_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
#         """处理礼物事件并广播给 WebSocket 客户端"""
#         data: Gift = Gift(**{
#             "room_id": client.room_id,
#             "uid": message.uid,
#             "uname": message.uname,
#             "gift_name": message.gift_name,
#             "num": message.num
#         })
#         # print(f'[礼物] {data}')
#         await broadcast(data, websocket_clients_current)


async def broadcast(message: Info, websocket_clients: Set[WebSocketResponse]):
    """向所有 WebSocket 客户端广播消息"""
    if websocket_clients:
        payload = json.dumps(str(message))
        print("开始广播", payload)
        result = await asyncio.gather(*[ws.send_str(payload) for ws in websocket_clients])
        print("广播结果", websocket_clients, result)


if __name__ == '__main__':
    asyncio.run(main())
