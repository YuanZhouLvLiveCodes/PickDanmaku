import json
import os
import asyncio
import ssl
import time

from aiohttp import web
import random
from typing import Optional

import aiohttp
import blivedm

import blivedm.models.web as web_models
from blivedm.handlers import logged_unknown_cmds
from live.api import PLATFORM_NAME, COMMAND_NAME
from live.api.bilibili import BiliPlatformApi
from live.model.bilibili import BiliCommand, BiliBuyGuard, BiliSuperChat, BiliGift, BiliDanmaku
from live.utils import get_user_path, download_file
from live.utils.aiohttp_utils import get_ssl_context, init_session
from live.utils.system_notice import Win11Notice

from config import SESSDATA, ROOM_INFOS, HTTP_HOST, HTTP_PORT, HTTP_SCHEME, SSL_CERT, SSL_KEY
from live.utils.ws_client.websocket_broadcast import broadcast, broadcast_text
from live.utils.ws_client.websocket_client import WebSocketClientSet, WebSocketClientDict
from live.utils.ws_client.websocket_danmaku import WebSocketDanmaku
from live.utils.ws_client.websocket_echo_live import WebSocketEchoLive
from live.utils.ws_client.websocket_pick_current import WebSocketPickCurrent

api = BiliPlatformApi()
api.login(type="qrcode")

ws_echo_live: WebSocketEchoLive = WebSocketEchoLive()
ws_pick_current: WebSocketPickCurrent = WebSocketPickCurrent()
ws_danmaku: WebSocketDanmaku = WebSocketDanmaku()


class PickDanmaku:
    session: Optional[aiohttp.ClientSession] = None  # HTTP 会话

    def __init__(self):
        pass


    async def get_room_infos(self, refresh=False):
        infos_dir = os.path.join(os.path.dirname(__file__), "assets", "meta")
        if not os.path.exists(infos_dir):
            os.makedirs(infos_dir)
        if refresh:
            for platform in ROOM_INFOS:
                for room_id in ROOM_INFOS[platform]:
                    time.sleep(random.randint(1, 10))
                    await self.get_room_info(room_id=room_id, platform=platform, refresh=refresh)

    async def main(self, refresh=False):
        print(api.cookies)
        self.session = init_session(session_data=api.cookies["SESSDATA"])
        await self.get_room_infos(refresh=refresh)
        # 启动 Web 服务
        app = web.Application()

        app.add_routes([
            # 提供 index.html 页面
            web.get('/', self.handle_index),
            # 提供 display.html 页面
            web.get('/display', self.handle_display),
            # 提供 WebSocket 服务
            web.get('/ws', ws_danmaku.handle_websocket),
            # 提供 WebSocket 服务
            web.get('/currentWs', ws_pick_current.handle_current),
            # 提供 WebSocket 服务
            web.get('/typeComment', ws_echo_live.handle_type_echo),
            # 处理静态资源请求
            web.get("/face/{uid}", api.handle_face),
            web.get("/face/{uid}/platform/{platform}", api.handle_face),
            web.get("/room/{room_id}", self.handle_room),
            web.get("/room/{room_id}/platform/{platform}", self.handle_room),
            web.get("/meta", self.handle_room_meta),
            web.get("/assets/{file_name}", self.handle_assets)
        ])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, HTTP_HOST, HTTP_PORT,
                           ssl_context=get_ssl_context() if HTTP_SCHEME == "https" else None)  # 在 localhost:8081 启动
        await site.start()
        print(f"Web server started at {HTTP_SCHEME}://{HTTP_HOST}:{str(HTTP_PORT)}")

        # 启动弹幕监听
        try:
            await self.run_blive_clients()
        finally:
            await self.session.close()

    async def handle_assets(self, request):
        """处理静态资源请求"""
        file_name = request.match_info['file_name']
        asset_path = str(os.path.join(os.path.dirname(__file__), 'assets', file_name))
        return web.FileResponse(asset_path)

    async def get_user_info(self, room_uid, platform, refresh=False):
        user_path = get_user_path(platform=platform, user_id=room_uid)
        if not refresh and os.path.exists(user_path):
            with open(user_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            if platform == "bilibili":
                user_info = await self.request_get(
                    f"https://api.live.bilibili.com/live_user/v1/Master/info?uid={room_uid}",
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
                room_data = await self.request_get(
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
            user_info = await self.get_user_info(room_uid, platform, refresh=refresh)
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
        await self.get_room_infos(refresh=refresh)

        return web.Response(status=200, body=json.dumps(ROOM_INFOS, ensure_ascii=False), headers={
            "Content-Type": "application/json; charset=utf-8"
        })

    async def handle_room(self, request):
        """处理静态资源请求"""
        room_id = request.match_info['room_id']
        platform = request.match_info.get('platform', 'bilibili')
        data = await self.get_room_info(room_id=room_id, platform=platform, refresh=True)
        return web.Response(status=200, body=json.dumps(data, ensure_ascii=False), headers={
            "Content-Type": "application/json; charset=utf-8"
        })

    async def download_file(self, download_url, save_path):
        try:
            async with self.session.get(download_url, timeout=10) as response:
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
            async with self.session.get(url, headers=headers) as response:
                return await response.json()
        except Exception as e:
            print(e)
            return None



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

    # 运行多个 B站直播间的弹幕监听
    async def run_blive_clients(self):
        danmaku_clients = [blivedm.BLiveClient(room_id, session=self.session) for room_id in
                           ROOM_INFOS.get("bilibili", [])]
        danmaku_handler = self.DanmakuHandler()
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
            room_info = api.get_room_info(room_id)
            room_title = room_info["room_title"]
            room_uid = room_info["room_uid"]
            room_uname = room_info["room_uname"]

            data: BiliDanmaku = BiliDanmaku(**{
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
            await broadcast(data, ws_danmaku.websocket_set)

        def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
            # 调度异步任务
            asyncio.create_task(self.handle_gift(client, message))

        async def handle_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
            """处理礼物事件并广播给 WebSocket 客户端"""
            room_info = api.get_room_info(client.room_id)
            data: BiliGift = BiliGift(**{
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
            await broadcast(data, ws_danmaku.websocket_set)

        def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
            # 调度异步任务
            asyncio.create_task(self.handle_super_chat(client, message))

        async def handle_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
            """处理醒目留言事件并广播给 WebSocket 客户端"""
            room_info = api.get_room_info(client.room_id)
            data: BiliSuperChat = BiliSuperChat(**{
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
            await broadcast(data, ws_danmaku.websocket_set)

        def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
            # 调度异步任务
            asyncio.create_task(self.handle_buy_guard(client, message))

        async def handle_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
            """处理上舰事件并广播给 WebSocket 客户端"""
            room_info = api.get_room_info(client.room_id)
            data: BiliBuyGuard = BiliBuyGuard(**{
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
            await broadcast(data, ws_danmaku.websocket_set)

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
            room_info = api.get_room_info(room_id, refresh=cmd == "ROOM_CHANGE")
            room_uname = room_info["room_uname"]
            room_uid = room_info["room_uid"]
            room_title = room_info["room_title"]
            data: BiliCommand = BiliCommand(**{
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
            await broadcast(data, ws_danmaku.websocket_set)


if __name__ == '__main__':
    pick_danmaku = PickDanmaku()
    asyncio.run(pick_danmaku.main(refresh=False))
    # asyncio.run(pick_danmaku.main(refresh=True))
