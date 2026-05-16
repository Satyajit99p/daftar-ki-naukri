import os
import time

import requests


def download_pdf(url: str, save_path: str):

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for attempt in range(3):
        try:
            response = requests.get(url, stream=True, timeout=(30, 120))
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as ex:
            if attempt < 2:
                time.sleep(2)
                continue
            raise

    content_type = response.headers.get("content-type", "")

    if "pdf" not in content_type.lower():
        raise Exception(f"Not a PDF: {url}")

    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"Downloaded: {save_path}")