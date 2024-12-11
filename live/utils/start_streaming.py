import json
import os
import time
from typing import Dict

import requests










if __name__ == '__main__':
    login_result = login(login_type="qrcode")
    print(login_result["cookies"])
    # stream_pass = get_current_stream_pass(cookies=login_result["cookies"])
    # print(stream_pass["data"])
    # identity_code = get_identity_code(cookies=login_result["cookies"])
    # print(identity_code["data"])
    # stop_result = stop_streaming(cookies=login_result["cookies"])
    # print(stop_result)
    change_area_result = change_area_by_code(cookies=login_result["cookies"])
    print(change_area_result)
    start_result = start_streaming(cookies=login_result["cookies"])
    print(start_result)

    # original_string = b"\xe5\x87\xba\xe9\x94\x99\xe5\x95\xa6"
    # string_bytes = original_string
    # string = string_bytes.decode('utf-8', 'ignore')
    # print(detect(string_bytes))
    # print(string, original_string)
