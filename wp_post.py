import requests as req
from config import get_req_headers, url

def post_image_to_server(file_path):

    media = {
        "file": open(file_path, "rb"),
    }

    response = req.post(url=url, headers = get_req_headers(), files=media)
    print(dict(response.json())["id"])
    return dict(response.json())["id"]