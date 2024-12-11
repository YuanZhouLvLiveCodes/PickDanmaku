from typing import Dict


def format_cookies(cookies_str: str) -> Dict:
    cookies_list = cookies_str.split(";")
    cookies = {}
    for cookie in cookies_list:
        key, value = cookie.split("=")
        cookies[key.strip()] = value.strip()
    return cookies
