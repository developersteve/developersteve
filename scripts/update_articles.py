#!/usr/bin/env python3
"""Refresh the "Latest writing" list in README.md from Medium + Clermont Digital.

Mirrors the Latest Articles feed on developersteve.com, except the Clermont
Digital feed is filtered to posts bylined exactly "Steven Coochin" (the agency
blog also carries posts by other people). Standard library only, so the
workflow needs no installs.

Run from anywhere:  python3 scripts/update_articles.py
"""
from __future__ import annotations

import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- LATEST-WRITING:START -->", "<!-- LATEST-WRITING:END -->"
MAX_POSTS = 6

FEEDS = [
    # (source label, feed URL, required dc:creator or None for any)
    ("Medium", "https://medium.com/feed/@developersteve", None),
    ("Clermont Digital", "https://clermontdigital.com.au/feed/", "Steven Coochin"),
]
DC = "{http://purl.org/dc/elements/1.1/}creator"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "developersteve-profile/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def posts_from(source: str, url: str, author: str | None) -> list[dict]:
    root = ET.fromstring(fetch(url))
    posts = []
    for item in root.iter("item"):
        creator = (item.findtext(DC) or "").strip()
        if author and creator != author:
            continue
        link = (item.findtext("link") or "").strip().split("?")[0]  # drop Medium's ?source= tracking
        posts.append({
            "title": " ".join((item.findtext("title") or "").split()),
            "link": link,
            "date": parsedate_to_datetime(item.findtext("pubDate")),
            "source": source,
        })
    return posts


def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())


def main() -> int:
    posts, seen = [], set()
    for source, url, author in FEEDS:
        try:
            posts.extend(posts_from(source, url, author))
        except Exception as exc:  # one feed down shouldn't blank the list
            print(f"warning: {source} feed failed: {exc}", file=sys.stderr)
    if not posts:
        print("no posts fetched; leaving README untouched", file=sys.stderr)
        return 0

    posts.sort(key=lambda p: p["date"], reverse=True)
    lines = []
    for p in posts:
        key = title_key(p["title"])
        if key in seen:  # the same piece cross-posted to both feeds
            continue
        seen.add(key)
        title = p["title"].replace("[", "(").replace("]", ")")
        lines.append(f"- [{title}]({p['link']}) <sub>{p['source']} · {p['date']:%-d %b %Y}</sub>")
        if len(lines) == MAX_POSTS:
            break

    readme = README.read_text(encoding="utf-8")
    block = f"{START}\n" + "\n".join(lines) + f"\n{END}"
    updated = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
    if updated != readme:
        README.write_text(updated, encoding="utf-8")
        print(f"README updated with {len(lines)} posts")
    else:
        print("README already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
