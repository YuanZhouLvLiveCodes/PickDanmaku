# 初始化 HTTP 会话
import ssl

import aiohttp

from config import SESSDATA, SSL_KEY, SSL_CERT


def init_session(session_data:str=SESSDATA) -> aiohttp.ClientSession:
    cookies = aiohttp.CookieJar()
    cookies.update_cookies({'SESSDATA': session_data})
    return aiohttp.ClientSession(cookie_jar=cookies)


# 主程序
def get_ssl_context() -> ssl.SSLContext:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)
    return ssl_context
