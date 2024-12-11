import os.path
from os.path import isdir

import requests

from os import PathLike


def download_file(download_url: str, file_path: PathLike) -> bool:
    """
    下载文件
    :param download_url: 下载链接
    :param file_path: 文件保存路径
    :return: 下载结果
    """
    try:
        file_name = os.path.basename(download_url)
        if isdir(file_path):
            file_path = os.path.join(file_path, file_name)

        with requests.get(download_url, stream=True) as r:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print(e)
        return False
