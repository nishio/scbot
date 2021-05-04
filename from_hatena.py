# -*- coding: utf-8 -*-
import scbio
import random
import json
import codecs
from collections import defaultdict
import re
import datetime
import html

lines = open("nishiohirokazu.xml")

ymd_to_body = {}
ymd_to_d = {}
ym_to_ymd = defaultdict(set)
y_to_ym = defaultdict(set)
md_to_ymd = defaultdict(set)


def parse_day():
    buf = []
    for line in lines:
        if line == "</day>\n":
            return buf
        buf.append(html.unescape(line))


for line in lines:
    print(line)
    m = re.match('<day date="([^"]+)"[^>]*>', line)
    if m:
        ymd = m.groups()[0]
        body = parse_day()

        ymd_to_body[ymd] = body
        y, m, d = ymd.split("-")
        ym = (y, m)
        ym_to_ymd[(y, m)].add(ymd)
        y_to_ym[y].add(ym)


pages = []


def timestamp(*args):
    return datetime.datetime(*map(int, args)).timestamp()


def add_page(title, lines, updated):
    page = dict(
        title=title,
        lines=[title] + lines,
        updated=updated)
    pages.append(page)


for y in y_to_ym:
    add_page(
        title=f"Hatena{y}",
        lines=[f"[Hatena{ym[0]}{ym[1]}]" for ym in sorted(y_to_ym[y])],
        updated=timestamp(y, 1, 1))

for ym in ym_to_ymd:
    y, m = ym
    add_page(
        title=f"Hatena{y}{m}",
        lines=["[Hatena%s]" % ymd for ymd in sorted(ym_to_ymd[ym])],
        updated=timestamp(y, m, 1))

for ymd in ymd_to_body:
    lines = ["code:hatena"]
    lines += [f" {line}" for line in ymd_to_body[ymd]]
    y, m, d = ymd.split("-")

    lines += ["",
              f"[はてなダイアリー {ymd} https://nishiohirokazu.hatenadiary.org/archive/{y}/{m}/{d}]"]
    add_page(
        title=f"Hatena{ymd}",
        lines=lines,
        updated=timestamp(y, m, d))


# random.seed(42)
# random.shuffle(pages)
# pages = pages[:10]

json.dump(
    dict(pages=pages),
    codecs.open('to_scrapbox.json', 'w', encoding="utf-8"),
    ensure_ascii=False, indent=2)

# print("importing...")
# scbio.import_to("nishio-hatena", json.dumps(dict(pages=pages)))
