#!/usr/bin/env python3
"""Refresh public repository dashboard in the profile README (stdlib only)."""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

USER = "ajaysingh132"
START = "<!-- AUTO-DASHBOARD:START -->"
END = "<!-- AUTO-DASHBOARD:END -->"
TOKEN = os.environ.get("GH_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "gbsbforyou-profile-dashboard"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30) as response:
        return json.load(response)

def clean(value):
    value = str(value or "").replace("|", "／").replace("\n", " ").replace("\r", " ")
    return re.sub(r"[<>]", "", value).strip()

def main():
    repos = []
    for page in range(1, 20):
        batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner&sort=updated")
        if not batch:
            break
        repos.extend(r for r in batch if not r.get("private") and not r.get("fork") and r.get("name") != USER)
        if len(batch) < 100:
            break
    repos.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    featured = [
        "GBSBFORYOU-Platform", "GBSBFORYOU-Digital-Gurukul-",
        "gbsbforyou-publications", "GBSB-AI-Media-Studio",
        "Banjara-Language-Engine-BLE-v1.0", "banjara-census-mission",
        "Maa-Sharda-General-Market-Place-", "allnews",
    ]
    by_name = {r["name"].lower(): r for r in repos}
    picks = [by_name[n.lower()] for n in featured if n.lower() in by_name]
    lines = [
        f"**Public original repositories:** {len(repos)}  ·  **Updated (UTC):** {datetime.now(timezone.utc):%Y-%m-%d %H:%M}",
        "",
        "### Featured projects",
        "| Project | Description |",
        "| --- | --- |",
    ]
    for r in picks:
        lines.append(f"| [{clean(r['name'])}]({r['html_url']}) | {clean(r.get('description')) or 'Explore the repository'} |")
    lines += ["", "### Recently active repositories", "| Repository | Language | Last push (UTC) |", "| --- | --- | --- |"]
    for r in repos[:15]:
        date = (r.get("pushed_at") or "—")[:10]
        lines.append(f"| [{clean(r['name'])}]({r['html_url']}) | {clean(r.get('language')) or '—'} | {date} |")
    lines += ["", f"[Browse all public repositories](https://github.com/{USER}?tab=repositories)"]
    path = "README.md"
    with open(path, encoding="utf-8") as f:
        original = f.read()
    if original.count(START) != 1 or original.count(END) != 1:
        raise RuntimeError("README dashboard markers missing or duplicated")
    replacement = START + "\n" + "\n".join(lines) + "\n" + END
    updated = original[:original.index(START)] + replacement + original[original.index(END) + len(END):]
    if updated != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)

if __name__ == "__main__":
    main()
