import json
import os
from typing import Dict, Callable, Optional

import aiohttp
import requests

from live.utils import dict_merge, format_cookies
from live.utils.get_path import get_user_path, get_room_path, get_cookies_path


class BasePlatform:
    BASE_HEADER: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 "
                      "Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # BASE_HEADERS = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #                   "AppleWebKit/537.36 (KHTML, like Gecko) "
    #                   "Chrome/91.0.4472.124 "
    #                   "Safari/537.36 "
    #                   "Edg/91.0.864.70",
    #     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    #     "Accept": "application/json, text/plain, */*",
    #     "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    #     # "Referer": "https://api.live.bilibili.com/",
    # }

    _cookies: Dict[str, str]

    def request_get(self, url, params=None, headers=None, *args, **kwargs):
        """
        发送get请求
        :param url: 请求地址
        :param params: 请求参数
        :param headers: 请求头
        :param kwargs: 其他参数
        :return: 请求结果
        """
        return requests.get(url=url, params=params, headers=dict_merge(self.BASE_HEADER, headers), *args, **kwargs)

    async def request_get_aiohttp(self, url, params=None, headers=None, *args, **kwargs):
        """
        发送get请求
        :param url: 请求地址
        :param params: 请求参数
        :param headers: 请求头
        :param args: 其他参数
        :param kwargs: 其他参数
        :return: 请求结果
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params, headers=dict_merge(self.BASE_HEADER, headers), *args,
                                   **kwargs) as response:
                return await response.text()

    def request_post(self, url, data=None, json=None, headers=None, *args, **kwargs):
        """
        发送post请求
        :param json: 请求json数据
        :param data: 请求form数据
        :param url: 请求地址
        :param headers: 请求头
        :param kwargs: 其他参数
        :return: 请求结果
        """
        return requests.post(url=url, data=data, json=json, headers=dict_merge(self.BASE_HEADER, headers), *args,
                             **kwargs)

    async def request_post_aiohttp(self, url, data=None, json=None, headers=None, *args, **kwargs):
        """
        发送post请求
        :param url: 请求地址
        :param data: 请求form数据
        :param json: 请求json数据
        :param headers: 请求头
        :param args: 其他参数
        :param kwargs: 其他参数
        :return: 请求结果
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data, json=json, headers=dict_merge(self.BASE_HEADER, headers), *args,
                                    **kwargs) as response:
                return await response.text()

    def __init__(self):
        self._cookies: Dict[str, str] = {}

    @property
    def cookies(self) -> Dict[str, str]:
        return self._cookies

    @cookies.deleter
    def cookies(self):
        del self._cookies

    @cookies.setter
    def cookies(self, cookies: Dict[str, str]):
        self._cookies = cookies

    def save_cookies(self, platform: str) -> bool:
        cookies_path = get_cookies_path(platform=platform)
        with open(cookies_path, "w", encoding="utf-8") as f:
            json.dump(self._cookies, f, ensure_ascii=False, indent=4)
            return True

    def load_cookies(self, platform: str) -> bool:
        cookies_path = get_cookies_path(platform=platform)
        if os.path.exists(cookies_path):
            with open(cookies_path, "r", encoding="utf-8") as f:
                file_text = f.read()
                try:
                    self._cookies = json.loads(file_text)
                except json.JSONDecodeError:
                    self._cookies = format_cookies(file_text)
                return True
        return False

    def login(self, **kwargs):
        raise NotImplementedError("子类必须实现该方法")

    def _get_user_info(self, platform: str, user_id: str) -> Optional[Dict]:
        """

        :param platform:
        :param user_id:
        :return:
        """
        try:
            user_path = get_user_path(platform=platform, user_id=user_id)
            if os.path.exists(user_path):
                with open(user_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"获取用户信息失败：{e}")
            return None

    def _get_room_info(self, platform: str, room_id: int) -> Optional[Dict]:
        """

        :param platform:
        :param room_id:
        :return:
        """
        meta_path = get_room_path(platform=platform, room_id=room_id)
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
