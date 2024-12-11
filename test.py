import json
import os
import asyncio
import ssl
import time

from aiohttp import web, WSMsgType
import random
from typing import Optional, Set, Dict

import aiohttp
import blivedm
from aiohttp.web_ws import WebSocketResponse

import blivedm.models.web as web_models
from blivedm.handlers import logged_unknown_cmds
from live.api import PLATFORM_NAME
from live.api.base_api import BasePlatform
from live.api.bilibili import BiliPlatformApi
from live.utils.system_notice import Win11Notice

from config import SESSDATA, ROOM_INFOS, HTTP_HOST, HTTP_PORT, HTTP_SCHEME, SSL_CERT, SSL_KEY


class PickDanmaku:
    session: Optional[aiohttp.ClientSession] = None  # HTTP 会话
    websocket_clients_danmaku: Set[WebSocketResponse] = set()  # WebSocket 客户端列表
    websocket_clients_current: Set[WebSocketResponse] = set()  # WebSocket 客户端列表
    websocket_clients_type_echo: Dict[str, WebSocketResponse] = dict()  # WebSocket 客户端列表

    api: BasePlatform

    def __init__(self):
        self.api = BiliPlatformApi()
        self.api.cookies = self.api.login(type="qrcode")


    async def get_room_infos(self, refresh=False):
        infos_dir = os.path.join(os.path.dirname(__file__), "assets", "meta")
        if not os.path.exists(infos_dir):
            os.makedirs(infos_dir)
        if refresh:
            for platform in ROOM_INFOS:
                for room_id in ROOM_INFOS[platform]:
                    time.sleep(random.randint(1, 10))
                    await self.get_room_info(room_id=room_id, platform=platform, refresh=refresh)

    # 初始化 HTTP 会话
    def init_session(self) -> aiohttp.ClientSession:
        cookies = aiohttp.CookieJar()
        cookies.update_cookies({'SESSDATA': SESSDATA})
        return aiohttp.ClientSession(cookie_jar=cookies)

    # 主程序
    def get_ssl_context(self) -> ssl.SSLContext:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)
        return ssl_context

    async def main(self, refresh=False):
        global session
        session = init_session()

        await get_room_infos(refresh=refresh)
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
            # 提供 WebSocket 服务
            web.get('/typeComment', handle_type_echo),
            # 处理静态资源请求
            web.get("/face/{uid}", handle_face),
            web.get("/face/{uid}/platform/{platform}", handle_face),
            web.get("/room/{room_id}", handle_room),
            web.get("/room/{room_id}/platform/{platform}", handle_room),
            web.get("/meta", handle_room_meta),
            web.get("/assets/{file_name}", handle_assets)
        ])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, HTTP_HOST, HTTP_PORT,
                           ssl_context=get_ssl_context() if HTTP_SCHEME == "https" else None)  # 在 localhost:8081 启动
        await site.start()
        print(f"Web server started at {HTTP_SCHEME}://{HTTP_HOST}:{str(HTTP_PORT)}")

        # 启动弹幕监听
        try:
            await run_blive_clients()
        finally:
            await session.close()

    async def handle_assets(self, request):
        """处理静态资源请求"""
        file_name = request.match_info['file_name']
        asset_path = str(os.path.join(os.path.dirname(__file__), 'assets', file_name))
        return web.FileResponse(asset_path)

    async def get_user_info(self, room_uid, platform, refresh=False):

        if not refresh and os.path.exists(user_path):
            with open(user_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            if platform == "bilibili":
                user_info = await request_get(f"https://api.live.bilibili.com/live_user/v1/Master/info?uid={room_uid}",
                                              headers={
                                                  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                                                  "Referer": "https://space.bilibili.com/" + str(room_uid)
                                              })

                uid = user_info["data"]["info"]["uid"]
                uname = user_info["data"]["info"]["uname"]
                face = user_info["data"]["info"]["face"]
                room_id = user_info["data"]["room_id"]
            else:
                uid = ""
                uname = ""
                face = ""
                room_id = ""
            user = {
                "uid": uid,
                "uname": uname,
                "face": face,
                "room_id": room_id,
            }
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(user, f, ensure_ascii=False, indent=4)
            return user
        pass

    async def get_room_info(self, room_id, platform, refresh=False):
        # assets/meta/{platform}/{room_id}.json
        meta_dir = str(os.path.join(os.path.dirname(__file__), 'assets', 'meta', platform))
        if not os.path.exists(meta_dir):
            os.makedirs(meta_dir)
        meta_path = str(os.path.join(meta_dir, f"{str(room_id)}.json"))
        if not refresh and os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            platform_name = PLATFORM_NAME.get(platform, platform)
            if platform == "bilibili":
                room_data = await request_get(
                    f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={str(room_id)}",
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                        "Referer": "https://live.bilibili.com/" + str(room_id)
                    })
                print(room_data)
                room_uid = room_data["data"]["uid"]
                room_title = room_data["data"]["title"]
                stream_status = room_data["data"]["live_status"] == 1
                area_name = room_data["data"]["parent_area_name"] + " / " + room_data["data"]["area_name"]
            else:
                room_title = ""
                stream_status = None
                area_name = ""
                room_uid = ""
            user_info = await get_user_info(room_uid, platform, refresh=refresh)
            room_uname = user_info["uname"]
            data = {
                "room_id": room_id,
                # "room_info": room_data,
                "room_title": room_title,
                "platform": platform,
                "platform_name": platform_name,
                "stream_status": stream_status,
                "area_name": area_name,
                "room_uid": room_uid,
                "room_uname": room_uname
            }
            if area_name != "":
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                # ROOM_INFOS[platform][room_id] = data
            return data

    async def handle_room_meta(self, request):
        """处理静态资源请求"""
        refresh = request.query.get("refresh", "false")
        if refresh.lower() in ["false", "null", "undefined", "none", "0"]:
            refresh = False
        else:
            refresh = True
        await get_room_infos(refresh=refresh)

        return web.Response(status=200, body=json.dumps(ROOM_INFOS, ensure_ascii=False), headers={
            "Content-Type": "application/json; charset=utf-8"
        })

    async def handle_room(self, request):
        """处理静态资源请求"""
        room_id = request.match_info['room_id']
        platform = request.match_info.get('platform', 'bilibili')
        data = await get_room_info(room_id=room_id, platform=platform, refresh=True)
        return web.Response(status=200, body=json.dumps(data, ensure_ascii=False), headers={
            "Content-Type": "application/json; charset=utf-8"
        })

    async def download_file(self, download_url, save_path):
        try:
            async with session.get(download_url, timeout=10) as response:
                with open(save_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
            return True
        except Exception as e:
            print(e)
            return False

    async def request_get(self, url, headers=None):
        try:
            async with session.get(url, headers=headers) as response:
                return await response.json()
        except Exception as e:
            print(e)
            return None

    async def handle_face(self, request):
        """处理头像资源请求"""
        uid = request.match_info['uid']
        platform = request.match_info.get('platform', 'bilibili')
        if not uid or not uid.isdigit():
            uid = "noface"
        parent_path = os.path.join(os.path.dirname(__file__), 'assets', "face", platform)
        if not os.path.exists(parent_path):
            os.mkdir(parent_path)
        fase_path = str(os.path.join(os.path.dirname(__file__), 'assets', "face", platform, uid))
        if uid == "noface":
            return web.Response(status=200, body=open(fase_path, 'rb').read(), content_type="image/jpeg")
        if not os.path.exists(fase_path):
            print("下载头像")
            if platform == "bilibili":
                data = await session.get(f"https://api.bilibili.com/x/space/app/index?mid={uid}",
                                         headers={
                                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                                             "Referer": "https://space.bilibili.com/" + uid + "/dynamic"
                                         }, timeout=10)
                data_json = await data.json()
                if data_json['code'] == 0:
                    fase_url = data_json['data']["info"]['face']
                    result = await download_file(fase_url, fase_path)
                    if result:
                        return web.Response(status=200, body=open(fase_path, 'rb').read(),
                                            content_type=data.content_type)
        else:
            return web.Response(status=200, body=open(fase_path, 'rb').read(), content_type="image/jpeg")

    # 提供 index.html
    async def handle_index(self, request):
        """提供 index.html 页面"""
        index_path = os.path.join(os.path.dirname(__file__), 'index.html')
        return web.FileResponse(index_path)

    # 提供 display.html
    async def handle_display(self, request):
        """提供 display.html 页面"""
        display_path = os.path.join(os.path.dirname(__file__), 'display.html')
        return web.FileResponse(display_path)

    # WebSocket 处理函数
    async def handle_websocket(self, request):
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
    async def handle_current(self, request):
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
                        websocket_clients_type_echo[from_uuid] = ws
                    elif data["action"] in ["hello"]:
                        print("hello from: " + from_uuid)
                        pass
                    else:
                        await broadcast_text(msg.data, websocket_clients_type_echo)

                elif msg.type == WSMsgType.ERROR:
                    print(f"当前消息 WebSocket 错误：{ws.exception()}")
        finally:
            for uuid, ws_client in websocket_clients_type_echo.items():
                if ws == ws_client:
                    del websocket_clients_type_echo[uuid]
                    break
            print("当前消息 WebSocket 客户端已断开")

        return ws

    # 运行多个 B站直播间的弹幕监听
    async def run_blive_clients(self):
        danmaku_clients = [blivedm.BLiveClient(room_id, session=session) for room_id in
                           ROOM_INFOS.get("bilibili", [])]
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
            room_id = client.room_id
            uname = message.uname
            uid = message.uid
            room_info = await get_room_info(room_id, "bilibili")
            room_title = room_info["room_title"]
            room_uid = room_info["room_uid"]
            room_uname = room_info["room_uname"]

            data: Danmaku = Danmaku(**{
                "room_id": room_id,
                "uname": uname,
                "uid": uid,
                "platform": "bilibili",
                "room_title": room_title,
                "room_uid": room_uid,
                "room_uname": room_uname,

                "msg": message.msg,
            })
            print(f'[弹幕] {data}')
            await broadcast(data, websocket_clients_danmaku)

        def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
            # 调度异步任务
            asyncio.create_task(self.handle_gift(client, message))

        async def handle_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
            """处理礼物事件并广播给 WebSocket 客户端"""
            room_info = await get_room_info(client.room_id, "bilibili")
            data: Gift = Gift(**{
                "room_id": client.room_id,
                "uname": message.uname,
                "uid": message.uid,
                "platform": "bilibili",
                "room_title": room_info["room_title"],
                "room_uid": room_info["room_uid"],
                "room_uname": room_info["room_uname"],

                "gift_name": message.gift_name,
                "num": message.num,
            })
            print(f'[礼物] {data}')
            await broadcast(data, websocket_clients_danmaku)

        def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
            # 调度异步任务
            asyncio.create_task(self.handle_super_chat(client, message))

        async def handle_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
            """处理醒目留言事件并广播给 WebSocket 客户端"""
            room_info = await get_room_info(client.room_id, "bilibili")
            data: SuperChat = SuperChat(**{
                "room_id": client.room_id,
                "uname": message.uname,
                "uid": message.uid,
                "platform": "bilibili",
                "room_title": room_info["room_title"],
                "room_uid": room_info["room_uid"],
                "room_uname": room_info["room_uname"],

                "msg": message.message,
                "price": message.price,
            })
            print(f'[醒目留言] {data}')
            await broadcast(data, websocket_clients_danmaku)

        def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
            # 调度异步任务
            asyncio.create_task(self.handle_buy_guard(client, message))

        async def handle_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
            """处理上舰事件并广播给 WebSocket 客户端"""
            room_info = await get_room_info(client.room_id, "bilibili")
            data: BuyGuard = BuyGuard(**{
                "room_id": client.room_id,
                "uname": message.username,
                "uid": message.uid,
                "platform": "bilibili",
                "room_title": room_info["room_title"],
                "room_uid": room_info["room_uid"],
                "room_uname": room_info["room_uname"],

                "guard_level": message.guard_level,
                "num": message.num,
                "price": message.price,
            })
            print(f'[上舰] {data}')
            await broadcast(data, websocket_clients_danmaku)

        def handle(self, client: blivedm.BLiveClient, command: dict):
            cmd = command.get('cmd', '')
            pos = cmd.find(':')  # 2019-5-29 B站弹幕升级新增了参数
            if pos != -1:
                cmd = cmd[:pos]

            if cmd not in self._CMD_CALLBACK_DICT:
                # 调度异步任务
                if cmd not in [
                    "STOP_LIVE_ROOM_LIST",
                    "WIDGET_BANNER",
                    "ONLINE_RANK_V2",
                    "ONLINE_RANK_COUNT",
                ]:
                    asyncio.create_task(self.handle_others(client, command))
                # 只有第一次遇到未知cmd时打日志
                if cmd not in logged_unknown_cmds:
                    # print('room=%d unknown cmd=%s, command=%s' % (client.room_id, cmd, command))
                    logged_unknown_cmds.add(cmd)
                return

            callback = self._CMD_CALLBACK_DICT[cmd]
            if callback is not None:
                callback(self, client, command)

        async def handle_others(self, client: blivedm.BLiveClient, command: dict):
            cmd = command["cmd"]
            room_id = client.room_id
            room_info = await get_room_info(room_id, "bilibili", refresh=cmd == "ROOM_CHANGE")
            room_uname = room_info["room_uname"]
            room_uid = room_info["room_uid"]
            room_title = room_info["room_title"]
            data: Command = Command(**{
                "room_id": room_id,
                "room_uname": room_uname,
                "room_uid": room_uid,
                "room_title": room_title,
                "platform": "bilibili",
                "original_data": command,
                "cmd": cmd,
                "msg": cmd,
            })
            if data.uid == "" or data.uid is None:
                if data.cmd == "INTERACT_WORD":
                    data.uid = command["data"]["uid"]
                else:
                    data.uid = data.room_uid
            # 超管警告及被切断直播处理
            if data.cmd == "WARNING":  # 被警告
                warning_message = data.msg
                print(f'房间 {room_uname}({room_title}) 被警告: {warning_message}')
                Win11Notice(title=f'房间 {room_uname}({room_title}) 被警告', body=warning_message).show_notice()
            elif data.cmd == "CUT_OFF" or data.cmd == "CUT_OFF_V2":  # 被切断直播
                print(f'房间 {room_uname}({room_title}) 被切断直播')
                Win11Notice(title=f'房间 {room_uname}({room_title}) 被切断直播', body="请检查直播状态").show_notice()
            print(
                f'[{COMMAND_NAME["bilibili"][cmd] if cmd in COMMAND_NAME["bilibili"] else cmd}]【{room_uname}|{room_title}】 {data}')
            await broadcast(data, websocket_clients_danmaku)

    async def broadcast(self, message: Message, websocket_clients: Set[WebSocketResponse]):
        """向所有 WebSocket 客户端广播消息"""
        if websocket_clients:
            payload = str(message)
            # print("开始广播", payload)
            result = await asyncio.gather(*[ws.send_str(payload) for ws in websocket_clients])
            # print("广播结果", websocket_clients, result)

    async def broadcast_text(self, payload: str, websocket_clients: Dict[str, WebSocketResponse]):
        """向所有 WebSocket 客户端广播消息"""
        if websocket_clients:
            payload_json = json.loads(payload)
            rather_than_uuid = payload_json["from"]["name"]
            # payload = json.dumps(str(message))
            print("开始广播" + str(payload))
            result = await asyncio.gather(
                *[ws.send_str(payload) for uuid, ws in websocket_clients.items() if uuid != rather_than_uuid])
            # print("广播结果", websocket_clients, result)


if __name__ == '__main__':
    pick_danmaku = PickDanmaku()
    asyncio.run(pick_danmaku.main(refresh=False))
    # asyncio.run(main(refresh=True))
