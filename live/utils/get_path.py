import os

BASE_PATH = r"D:\Programming\PycharmProjects\pickDanmaku"


def get_user_path(platform, user_id):
    """
    获取缓存用户信息路径
    :param platform:
    :param user_id:
    :return:
    """
    user_dir = str(os.path.join(BASE_PATH, 'assets', 'user', platform))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return str(os.path.join(user_dir, f"{user_id}.json"))


def get_room_path(platform: str, room_id: int):
    """
    获取缓存用户信息路径
    :param platform:
    :param room_id:
    :return:
    """
    user_dir = str(os.path.join(BASE_PATH, 'assets', 'meta', platform))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return str(os.path.join(user_dir, f"{str(room_id)}.json"))


def get_cookies_path(platform: str):
    cookies_dir = str(os.path.join(BASE_PATH, 'assets', 'cookies'))
    if not os.path.exists(cookies_dir):
        os.makedirs(cookies_dir)
    return str(os.path.join(cookies_dir, f"{platform}.txt"))


def get_base_path():
    return BASE_PATH


def get_temp_path():
    temp_dir = os.path.join(BASE_PATH, 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir
