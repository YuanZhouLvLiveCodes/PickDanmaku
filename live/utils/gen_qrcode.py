import os
import tempfile
import time

import qrcode

from qrcode.image.pure import PyPNGImage
from io import BytesIO

# from qrcode.main import GenericImage

from live.utils.get_path import get_base_path, get_temp_path


def to_qrcode(url) -> PyPNGImage:
    url_qrcode_value: PyPNGImage = qrcode.make(url)
    return url_qrcode_value


def show_image(image: bytes):
    # 生成随机文件名的图片到临时目录
    temp_path = get_temp_path()
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", dir=temp_path, delete=False)
    temp_file.write(image)
    temp_file.flush()
    temp_file.close()

    temp_file_path = os.path.join(temp_path, temp_file.name)

    # Debugging step: check the full file path
    print(f"Image saved at: {temp_file_path}")

    print(f"start '{temp_file_path}'")

    # Ensure path is quoted correctly
    os.system(f'start "" "{temp_file_path}"')


def read_py_png_image(py_png_image: PyPNGImage) -> bytes:
    with BytesIO() as output:
        py_png_image.save(output)
        image_bytes_data = output.getvalue()
    return image_bytes_data

    pass
