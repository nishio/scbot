import requests
from dotenv import load_dotenv
import json
import os

load_dotenv()

API_ME = "https://scrapbox.io/api/users/me"
API_IMPORT = "https://scrapbox.io/api/page-data/import/{project}.json"

# init
sid = os.getenv("SID")
cookie = "connect.sid=" + sid
project = os.getenv("PROJECT")
project = "nishio-hatena"


def import_to(project, data):
    """
    data: string
    """
    r = requests.get(API_ME, headers={"Cookie": cookie})
    r.raise_for_status()
    csrfToken = r.json()["csrfToken"]

    url = API_IMPORT.format(project=project)
    r = requests.post(
        url,
        files={"import-file": data},
        headers={
            "Cookie": cookie,
            "Accept": "application/json, text/plain, */*",
            "X-CSRF-TOKEN": csrfToken,
        }
    )
    r.raise_for_status()


def write_pages(pages):
    data = json.dumps({"pages": pages})
    import_to(project, data)


def _test():
    pages = [
        {
            "title": "Scbot Home",
            "lines": ["Scbot Home", "Hello world!"]
        }
    ]
    write_pages(pages)
