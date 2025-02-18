import base64
import json
import os.path
import tempfile
import time
from typing import Dict, Union, Literal

from aiohttp import web
from aiohttp.client import _BaseRequestContextManager

from live.api import PLATFORM_NAME
from live.api.base_api import BasePlatform
from live.utils import (
    get_user_path,
    get_room_path,
    to_qrcode,
    read_py_png_image,
    show_image,
    get_cookies_path, dict_merge, format_cookies, download_file
)
from live.utils.get_path import get_temp_path
from live.utils.run_command import subprocess_run


class BiliPlatformApi(BasePlatform):

    def __init__(self):
        super().__init__()
        self.platform = 'bilibili'

    def get_user_info(self, user_id: str, refresh=False) -> Dict:
        if not refresh:
            local_result = self._get_user_info(
                platform=self.platform,
                user_id=user_id
            )
            if local_result is not None:
                return local_result
        url = f"https://api.live.bilibili.com/live_user/v1/Master/info?uid={str(user_id)}"
        online_result = self.request_get(url=url, headers={
            "Referer": "https://space.bilibili.com/" + str(user_id),
        }, cookies=self.cookies)
        uid = online_result["data"]["info"]["uid"]
        uname = online_result["data"]["info"]["uname"]
        face = online_result["data"]["info"]["face"]
        room_id = online_result["data"]["room_id"]
        user_info = {
            "uid": uid,
            "uname": uname,
            "face": face,
            "room_id": room_id,
        }
        with open(get_user_path(platform=self.platform, user_id=user_id), "w", encoding="utf-8") as f:
            json.dump(user_info, f, ensure_ascii=False, indent=4)
        return user_info

    def get_room_info(self, room_id: int, refresh=False) -> Dict:
        if not refresh:
            local_result = self._get_room_info(
                platform=self.platform,
                room_id=room_id
            )
            if local_result is not None:
                return local_result
        url = f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={str(room_id)}"
        online_result = self.request_get(url=url, headers={
            "Referer": "https://live.bilibili.com/" + str(room_id),
        })
        room_uid = online_result["data"]["uid"]
        room_title = online_result["data"]["title"]
        stream_status = online_result["data"]["live_status"] == 1
        area_name = online_result["data"]["parent_area_name"] + " / " + online_result["data"]["area_name"]
        user_info = self.get_user_info(room_uid, refresh=refresh)
        room_uname = user_info["uname"]
        platform_name = PLATFORM_NAME.get(self.platform, self.platform)
        room_info = {
            "room_id": room_id,
            # "room_info": online_result,
            "room_title": room_title,
            "platform": self.platform,
            "platform_name": platform_name,
            "stream_status": stream_status,
            "area_name": area_name,
            "room_uid": room_uid,
            "room_uname": room_uname
        }
        with open(get_room_path(platform=self.platform, room_id=room_id), "w", encoding="utf-8") as f:
            json.dump(room_info, f, ensure_ascii=False, indent=4)
        return room_info

    def login(self, login_type: Literal["cookie_str", "qrcode", "cookie"] = "qrcode", **kwargs) -> Dict:
        # 验证是否登录
        if self.get_current_user_info(cookies=self.cookies)["login"]:
            return {
                "code": 200,
                "message": "login success",
                "cookies": self.cookies
            }
        # 当前未登录尝试读取cookie文件
        cookies_path = get_cookies_path(platform=self.platform)
        print(cookies_path)
        if os.path.exists(cookies_path):
            self.load_cookies(platform=self.platform)
        # 验证读取cookie文件后是否登录
        if self.get_current_user_info(cookies=self.cookies)["login"]:
            return {
                "code": 200,
                "message": "login success",
                "cookies": self.cookies
            }

        # 仍未登录，执行正常登录流程
        if login_type == "cookie_str" or login_type == "cookies":
            cookie_str = kwargs.get("cookie_str", "")
            if cookie_str:
                self.cookies = format_cookies(cookie_str)
            else:
                self.cookies = kwargs.get("cookies", {})
            # 验证读取cookie参数后是否登录
            if self.get_current_user_info(cookies=self.cookies)["login"]:
                self.save_cookies(platform=self.platform)
                return {
                    "code": 200,
                    "message": "login success",
                    "cookies": self.cookies
                }
            # if os.path.exists(cookies_path):
            # with open(cookies_path, "r", encoding="utf-8") as f:
            #     cookies_str = f.read()
            # cookies = json.loads(cookies_str)
            # user_info_result: Dict[str, Union[int, str, bool, Dict]] = self.get_current_user_info(cookies=cookies)
            # if user_info_result["login"]:
            #     return {
            #         "code": 200,
            #         "message": "login success",
            #         "cookies": cookies
            #     }
        elif login_type == "qrcode":
            url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header&go_url=https:%2F%2Fwww.bilibili.com%2Fuser%2Flogin"
            response = self.request_get(url)
            response_data = response.json()
            qrcode_key = response_data["data"]["qrcode_key"]
            qrcode_url = response_data["data"]["url"]

            qrcode_img = to_qrcode(url=qrcode_url)

            image_data = read_py_png_image(py_png_image=qrcode_img)
            show_image(image_data)

            url = f"https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}&source=main-fe-header"
            while True:
                time.sleep(1)
                response = self.request_get(url)
                response_data = response.json()
                print(response_data)
                if response_data["data"]["code"] == 86101:
                    # 未扫码
                    continue
                if response_data["data"]["code"] == 86038:
                    # 二维码失效,已扫码未确认+未扫码都算过期
                    return {
                        "code": 400,
                        "message": "qrcode expired"
                    }
                if response_data["data"]["code"] == 86090:
                    # 已扫码未确认
                    continue
                if response_data["data"]["code"] == 0:
                    # 已确认
                    # if response_data["data"]["url"] != '':
                    #     qrcode_img2 = to_qrcode(url=response_data["data"]["url"])
                    #     image_data2 = read_py_png_image(py_png_image=qrcode_img2)
                    #     show_image(image_data2)
                    # else:
                    self.cookies = response.cookies.get_dict()
                    self.save_cookies(platform=self.platform)
                    return {
                        "code": 200,
                        "message": "login success",
                        "cookies": self.cookies
                    }

        pass


    async def handle_face(self, request):
        """处理头像资源请求"""
        uid = request.match_info['uid']
        platform = request.match_info.get('platform', 'bilibili')
        if not uid or not uid.isdigit():
            uid = "noface"
        parent_path = os.path.join(os.getcwd(), 'assets', "face", platform)
        if not os.path.exists(parent_path):
            os.mkdir(parent_path)
        fase_path = str(os.path.join(os.getcwd(), 'assets', "face", platform, uid))
        if uid == "noface":
            return web.Response(status=200, body=open(fase_path, 'rb').read(), content_type="image/jpeg")
        if not os.path.exists(fase_path):
            print("下载头像")
            if platform == "bilibili":
                data = self.request_get(f"https://api.bilibili.com/x/space/app/index?mid={uid}",
                                              headers={
                                                  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                                                  "Referer": "https://space.bilibili.com/" + uid + "/dynamic"
                                              }, timeout=10)
                data_json = data.json()
                if data_json['code'] == 0:
                    fase_url = data_json['data']["info"]['face']
                    result = download_file(fase_url, fase_path)
                    if result:
                        return web.Response(status=200, body=open(fase_path, 'rb').read())
        else:
            return web.Response(status=200, body=open(fase_path, 'rb').read(), content_type="image/jpeg")
    def get_current_user_info(self, cookies=None) -> Union[
        Dict[str, Union[int, str, bool, Dict]]
    ]:
        url = "https://api.bilibili.com/x/web-interface/nav"
        response = self.request_get(url, cookies=cookies)
        response_data = response.json()
        if response_data["code"] == 0:
            data = {
                "code": 200,
                "message": "login success",
                "data": response_data["data"],
                "login": True
            }
        else:
            data = {
                "code": 400,
                "message": "login failed",
                "data": response_data["message"],
                "login": False
            }
        print(data)
        return data

    def verify_has_csrf_token(self) -> bool:
        return "bili_jct" in self.cookies.keys()

    async def start_streaming(self, room_id: int = 8487238) -> Dict:
        if not self.verify_has_csrf_token():
            return {
                "code": 400,
                "message": "csrf token not found in cookies"
            }
        url = f"https://api.live.bilibili.com/v1/Room/startLive"
        # url = f"https://api.mineserv.cn/db_manage.php?debug=1"
        response_text:str = await self.request_post_aiohttp(
            url,
            cookies=self.cookies,
            # cookies=format_cookies("buvid3=EFC6335F-3E3E-13B0-F2D7-141B07F3369E72373infoc; b_nut=1733879372; buvid4=0FC10218-2332-BCB8-A8E1-63810153463772373-024121101-ginkArCqs4cEtL6kWZVMjCO6zkWnkDk5unwPZmB4TJ6oxPy2IJQo5SxZTVdsB4TT; LIVE_BUVID=AUTO7517338793733338; SESSDATA=f290e04f%2C1749431386%2C9487b%2Ac2CjCIEnZK7nCdedaA0i6H1DYtWzEqTWyD9R9XsT6dvhnS3cI2K18E4h0-nQ32pf0Kw0wSVk1zYmJEd1BJLXdqT0NOcnpONGIyaWQ0V0FqU0ZUZFVDUmNMLVNDaDF3djhsNzV5UkQxcEcwczRoelY5UXF4QU5wZ3FueFhVX3o4dDBxTVJ4c0RhYWVBIIEC; bili_jct=24a7cabc3367ed506ed46cc5742b00b6; DedeUserID=269755531; DedeUserID__ckMd5=dbf9600a3a0d2377; _uuid=EA4B29D2-4F92-B4E9-2A210-E3A53EAFE6DD86397infoc; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQxMzg1ODgsImlhdCI6MTczMzg3OTMyOCwicGx0IjotMX0.KxNPOZNj19OCZcG2nH20HSS_zUWd2ppt1-1Dt7I5mdU; bili_ticket_expires=1734138528; buvid_fp=276963493bc68fc340ae064c30de1034; b_lsid=5BAE1F710_193B3E8BA98; header_theme_version=CLOSE; enable_web_push=DISABLE; home_feed_column=4; browser_resolution=1280-699; CURRENT_FNVAL=2000; sid=8bz1cnkf; bp_t_offset_269755531=1009544720193421312; PVID=3"),
            data={
                "room_id": str(room_id),
                "platform": "pc",
                "area_v2": "371",  # 虚拟主播
                "backup_stream": "0",
                "csrf_token": self.cookies["bili_jct"],
                "csrf": self.cookies["bili_jct"]
            },
            # data="room_id=8487238&platform=pc&area_v2=371&backup_stream=0&csrf_token=24a7cabc3367ed506ed46cc5742b00b6"
            #      "&csrf=24a7cabc3367ed506ed46cc5742b00b6",
            headers={
                "Referer": "https://link.bilibili.com/p/center/index",
                # "Content-Type": "application/json",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://link.bilibili.com",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
            }
        )
        # print(response.request.body, response.request.headers)
        # response_text = await response.text()
        response_bytes = response_text.encode("utf-8")
        try:
            response_data = json.loads(response_text)
            if response_data["code"] == 0:
                return {
                    "code": 200,
                    "message": "start streaming success",
                    "data": response_data["data"]
                }
            else:
                return {
                    "code": 400,
                    "message": "start streaming failed",
                    "data": response_data["message"]
                }
        except json.JSONDecodeError:
            temp_path = get_temp_path()
            temp_file = tempfile.NamedTemporaryFile("wb", suffix=".html", delete=False, dir=temp_path)
            temp_file.write(response_bytes)
            temp_file.flush()
            temp_file.close()
            temp_file_path = os.path.join(temp_path, temp_file.name)
            print(f"temp file: {temp_file_path}")
            # os.system(f"start {temp_file_path}")
            # 处理控制台乱码 运行 temp_file_path
            subprocess_run(f"{temp_file_path}")
            print("json parse failed", response_text)
            return {
                "code": 400,
                "message": "json parse failed",
                # "data": response_text
            }

    def stop_streaming(self, room_id: int = 8487238) -> Dict:
        if not self.verify_has_csrf_token():
            return {
                "code": 400,
                "message": "csrf token not found in cookies"
            }
        url = f"https://api.mineserv.cn/db_manage.php"
        # url = f"https://api.live.bilibili.com/v1/Room/stopLive"
        response = self.request_post(url, cookies=self.cookies, data={
            "debug": 1,
            "room_id": room_id,
            "platform": "pc",
            "csrf_token": self.cookies["bili_jct"],
            "csrf": self.cookies["bili_jct"]
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })
        response_text = response.text
        response_bytes = response.content
        print(response_text)
        try:
            response_data = json.loads(response_text)
            if response_data["code"] == 0:
                return {
                    "code": 200,
                    "message": "stop streaming success",
                    "data": response_data["data"]
                }
            else:
                return {
                    "code": 400,
                    "message": "stop streaming failed",
                    "data": response_data["message"]
                }
        except json.JSONDecodeError:
            temp_path = get_temp_path()
            temp_file = tempfile.NamedTemporaryFile("wb", suffix=".html", delete=False, dir=temp_path)
            temp_file.write(response_bytes)
            temp_file_path = os.path.join(temp_path, temp_file.name)
            print(f"temp file: {temp_file_path}")
            subprocess_run(f"{temp_file_path}")
            print("json parse failed", response_text)
            return {
                "code": 400,
                "message": "json parse failed",
                # "data": response_text
            }



    def get_identity_code(self) -> Dict:
        url = "https://api.live.bilibili.com/xlive/open-platform/v1/common/operationOnBroadcastCode"
        response = self.request_post(url, cookies=self.cookies, data={
            "action": 1,
            "csrf_token": self.cookies["bili_jct"],
            "csrf": self.cookies["bili_jct"]
        })
        response_data = response.json()
        if response_data["code"] != 0:
            data = {
                "code": 400,
                "message": "get identity code failed",
                "data": response_data["message"]
            }
        else:
            data = {
                "code": 200,
                "message": "get identity code success",
                "data": response_data["data"]["code"]
            }
        return data

    def get_current_stream_pass(self) -> Dict:
        url = f"https://api.live.bilibili.com/xlive/app-blink/v1/live/FetchWebUpStreamAddr"
        response = self.request_post(url, cookies=self.cookies, data={
            "platform": "pc",
            "backup_stream": 0,
            "csrf_token": self.cookies["bili_jct"],
            "csrf": self.cookies["bili_jct"]
        })
        response_data = response.json()
        if response_data["code"] != 0:
            if response_data["code"] == -111:
                # 删除 cookies.txt
                os.remove(get_cookies_path(self.platform))
            return {
                "code": 400,
                "message": "get current stream pass failed",
                "data": response_data["message"]
            }
        else:
            response_data = response_data["data"]
            return {
                "code": 200,
                "message": "get current stream pass success",
                "data": response_data["addr"]["code"]
            }

    def change_area_by_code(self, area_id: str = "371", area_parent_id: str = "9") -> Dict:
        url = f"https://api.live.bilibili.com/xlive/app-blink/v1/index/getNewRoomSwitch"
        response = self.request_get(url, cookies=self.cookies, params={
            "area_id": area_id,
            "area_parent_id": area_parent_id,
            "platform": "pc"
        }, headers={
            "Referer": "https://link.bilibili.com/p/center/index",
            "Origin": "https://link.bilibili.com"
        })
        response_data = response.json()
        if response_data["code"] != 0:
            return {
                "code": 400,
                "message": "change area failed",
                "data": response_data["message"]
            }
        else:
            return {
                "code": 200,
                "message": "change area success",
                "data": response_data["data"]
            }

    def get_area_list(self) -> Dict:
        url = f"https://api.live.bilibili.com/room/v1/Area/getList?show_pinyin=1"
        response = self.request_get(url, cookies=self.cookies)
        response_data = response.json()
        return response_data["data"]

    def get_live_status(self, room_id: int = 8487238) -> int:
        url = f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={str(room_id)}"
        response = self.request_get(url, cookies=self.cookies)
        response_data = response.json()
        if response_data["code"] != 0:
            return -1
        else:
            return response_data["data"]["room_info"]["live_status"]

    def gen_web_token(self) -> Dict:
        url = f"https://api.bilibili.com/bapis/bilibili.api.ticket.v1.Ticket/GenWebTicket"
        timestamp_str = str(int(time.time()))
        response = self.request_post(url, cookies=self.cookies,
                                     params=f"key_id=ec02&"
                                            f"hexsign={self.gen_hex_sign(timestamp=timestamp_str)}&"
                                            f"context[ts]={timestamp_str}&"
                                            f"csrf=" + self.cookies["bili_jct"],
                                     # no_use={
                                     #     "key_id": "ec02",
                                     #     # "context": {
                                     #     #     "ts": timestamp_str,
                                     #     # },
                                     #     "context[ts]": {
                                     #         "ts": timestamp_str,
                                     #     },
                                     #     "csrf": self.cookies["bili_jct"],
                                     #     "hexsign": self.gen_hex_sign(timestamp=timestamp_str)
                                     # },

                                     headers={
                                         "Origin": "https://link.bilibili.com",
                                         "Referer": "https://link.bilibili.com/p/center/index",
                                         "Accept": "*/*",
                                         "Accept-Encoding": "gzip, deflate, br, zstd",
                                         "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en;q=0.7",
                                         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                     })
        # print(response.request.body, response.request.headers)
        response_data = response.json()
        # print(response_data)
        if response_data["code"] != 0:
            return {
                "code": 400,
                "message": "gen web token failed",
                "data": response_data["message"]
            }
        else:
            return {
                "code": 200,
                "message": "gen web token success",
                "data": response_data["data"]
            }

    def gen_hex_sign(self, timestamp):
        import hashlib
        import hmac
        # const t = CryptoJS.HmacSHA256(`ts{timestamp}`, (e => {
        #                 let t = "";
        #                 for (let n = 0; n < e.length; n++)
        #                     t += String.fromCharCode(e.charCodeAt(n) - 1);
        #                 return t
        #             }
        #             )("YhxToH[2q"))
        # return CryptoJS.enc.Hex.stringify(t)
        passcode = ""
        gen_passcode = "YhxToH[2q"
        for i in range(len(gen_passcode)):
            passcode += chr(ord(gen_passcode[i]) - 1)
        # print(passcode)
        hmac_message = hmac.new(key=bytes(passcode, 'UTF-8'), msg=f"ts{timestamp}".encode('utf-8'),
                                digestmod=hashlib.sha256).digest()
        return hmac_message.hex()


if __name__ == '__main__':
    # os.remove(get_temp_path())
    bili = BiliPlatformApi()
    # login_result = bili.login(login_type="qrcode")
    login_result = bili.login(login_type="cookie_str",
                              cookie_str="buvid3=EFC6335F-3E3E-13B0-F2D7-141B07F3369E72373infoc; b_nut=1733879372; "
                                         "buvid4=0FC10218-2332-BCB8-A8E1-63810153463772373-024121101-ginkArCqs4cEt"
                                         "L6kWZVMjCO6zkWnkDk5unwPZmB4TJ6oxPy2IJQo5SxZTVdsB4TT; "
                                         "LIVE_BUVID=AUTO7517338793733338; "
                                         "SESSDATA=f290e04f%2C1749431386%2C9487b%2Ac2CjCIEnZK7nCdedaA0i6H1DYtWzEqT"
                                         "WyD9R9XsT6dvhnS3cI2K18E4h0-nQ32pf0Kw0wSVk1zYmJEd1BJLXdqT0NOcnpONGIyaWQ0V"
                                         "0FqU0ZUZFVDUmNMLVNDaDF3djhsNzV5UkQxcEcwczRoelY5UXF4QU5wZ3FueFhVX3o4dDBxT"
                                         "VJ4c0RhYWVBIIEC; "
                                         "bili_jct=24a7cabc3367ed506ed46cc5742b00b6; DedeUserID=269755531; "
                                         "DedeUserID__ckMd5=dbf9600a3a0d2377; _uuid=EA4B29D2-4F92-B4E9-2A210-E3A53E"
                                         "AFE6DD86397infoc; "
                                         "bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAi"
                                         "OjE3MzQxMzg1ODgsImlhdCI6MTczMzg3OTMyOCwicGx0IjotMX0.KxNPOZNj19OCZcG2nH20H"
                                         "SS_zUWd2ppt1-1Dt7I5mdU; "
                                         "bili_ticket_expires=1734138528; buvid_fp=276963493bc68fc340ae064c30de1034; "
                                         "b_lsid=5BAE1F710_193B3E8BA98; header_theme_version=CLOSE; "
                                         "enable_web_push=DISABLE; home_feed_column=4; browser_resolution=1280-699; "
                                         "CURRENT_FNVAL=2000; sid=8bz1cnkf; "
                                         "bp_t_offset_269755531=1009544720193421312; PVID=3")
    # print(login_result)
    bili.cookies = login_result["cookies"]
    web_token_result = bili.gen_web_token()
    # print(web_token_result)
    ticket = web_token_result["data"]["ticket"]
    # print(ticket)
    ticket_expire = web_token_result["data"]["created_at"] + web_token_result["data"]["ttl"]
    # print(ticket_expire)
    new_obj = {
        "bili_ticket": ticket,
        "bili_ticket_expires": str(ticket_expire)
    }
    # print(type(new_obj["bili_ticket"]), new_obj["bili_ticket"])
    # print(type(new_obj["bili_ticket_expires"]), new_obj["bili_ticket_expires"])
    # print(type(bili.cookies["bili_jct"]), bili.cookies["bili_jct"])
    bili.cookies.update(new_obj)
    print(bili.cookies)
    # room_status_result = bili.get_live_status()
    # print(room_status_result)
    # area_list_result = bili.get_area_list()
    # print(area_list_result)

    # identity_code = bili.get_identity_code()
    # print(identity_code["data"])
    stop_result = bili.stop_streaming()
    print(stop_result)

    # change_area_result = bili.change_area_by_code()
    # print(change_area_result)
    # start_result = bili.start_streaming()
    # print(start_result)
    # gen_hex_sign_result = bili.gen_hex_sign(timestamp="1733879387")
    # print(gen_hex_sign_result)
