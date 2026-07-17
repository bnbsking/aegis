from typing import Dict, List

import requests


def request_ocr(
        bytes_list: List[bytes],
        url: str,
        extra_msg: str = "none"
    ) -> str | List | Dict | None:
    if not bytes_list:
        return None
    files = [("files", bytes_) for bytes_ in bytes_list]
    data = {"extra_msg": extra_msg}
    response = requests.post(url, files=files, data=data)
    return response.json()
