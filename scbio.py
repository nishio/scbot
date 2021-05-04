import requests
from dotenv import load_dotenv
import json
import os
from datetime import datetime
from collections import defaultdict
load_dotenv()

API_ME = "https://scrapbox.io/api/users/me"
API_IMPORT = "https://scrapbox.io/api/page-data/import/{project}.json"
API_PAGE_LIST = "https://scrapbox.io/api/pages/{project}"
API_PAGE = "https://scrapbox.io/api/pages/{project}/{title}"
API_QUERY = "https://scrapbox.io/api/pages/{project}/search/query"

# init
sid = os.getenv("SID")
cookie = "connect.sid=" + sid
r = requests.get(API_ME, headers={"Cookie": cookie})
r.raise_for_status()
csrfToken = r.json()["csrfToken"]


def import_to(project, data):
    """
    data: string
    """

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


def get_page_list(project):
    url = API_PAGE_LIST.format(project=project)
    r = requests.get(
        url,
        headers={
            "Cookie": cookie,
            "Accept": "application/json, text/plain, */*",
            "X-CSRF-TOKEN": csrfToken,
        }
    )
    r.raise_for_status()
    return r


def get_page(project, title):
    url = API_PAGE.format(project=project, title=title)
    r = requests.get(
        url,
        headers={
            "Cookie": cookie,
            "Accept": "application/json, text/plain, */*",
            "X-CSRF-TOKEN": csrfToken,
        }
    )
    r.raise_for_status()
    return r


def query(project, q, skip=0, sort="pageRank", limit=100):
    url = API_QUERY.format(project=project)
    r = requests.get(
        url,
        params=dict(q=q, skip=skip, sort=sort, limit=limit),
        headers={
            "Cookie": cookie,
            "Accept": "application/json, text/plain, */*",
            "X-CSRF-TOKEN": csrfToken,
        }
    )
    r.raise_for_status()
    return r


def write_pages(project, pages):
    data = json.dumps({"pages": pages})
    import_to(project, data)


def get_recent_pages(project):
    r = get_page_list("nishio")
    data = r.json()
    pages = data["pages"]
    now = datetime.now()
    for p in pages:
        updated = datetime.fromtimestamp(p["updated"])
        if (now - updated).days < 1:
            yield p


def get_recent_keyword(project):
    link_to = defaultdict(list)
    for page in get_recent_pages(project):
        title = page["title"]
        print(title)
        page = get_page(project, title).json()
        links = page["links"]
        for k in links:
            link_to[k].append(title)

    return link_to


def ex1():
    active_project = os.getenv("ACTIVE_PROJECT")
    target_projects = os.getenv("TARGET_PROJECTS").split(",")
    target_project = target_projects[0]
    output_project = os.getenv("OUTPUT_PROJECT")

    link_to = get_recent_keyword(active_project)
    lines = []
    print("-----\n\n")
    for keyword in link_to:
        data = query(target_project, keyword).json()
        query_link = f"[query https://scrapbox.io/{target_project}/search/page?q={keyword}]"
        if data["count"] > 0:
            lines.append(
                f"[{keyword}]:"
            )
            lines.append(
                f" [/{target_project}/{keyword}]({query_link}: {data['count']} hits)"
            )
            if data["count"] > 7:
                # too many
                pass
            else:
                for page in data["pages"]:
                    title = page['title']
                    lines.append(f" [/{target_project}/{title}]:")
                    for line in page["lines"]:
                        lines.append(f"  `{line}`")
    print("\n".join(lines))

    # write_pages(output_project, dict(title="tmp", lines=lines))


def _test():
    pages = [
        {
            "title": "Scbot Home",
            "lines": ["Scbot Home", "Hello world!"]
        }
    ]
    write_pages("nishio", pages)
