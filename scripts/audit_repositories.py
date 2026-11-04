#!/usr/bin/env python3
"""Audit public repositories for documentation gaps and broken local references."""
import json, os, re, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
USER = "ajaysingh132"
TOKEN = os.getenv("GH_TOKEN", "")
HEADERS = {"Accept":"application/vnd.github+json","User-Agent":"gbsbforyou-repository-auditor"}
if TOKEN: HEADERS["Authorization"] = "Bearer " + TOKEN

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=40) as res:
        return json.load(res)

def api_repos():
    out=[]
    for page in range(1,10):
        batch=get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner&sort=updated")
        if not batch: break
        out.extend(r for r in batch if not r.get("private") and not r.get("fork") and r["name"] != USER)
        if len(batch)<100: break
    return out

def audit(repo):
    name=repo["name"]; branch=repo.get("default_branch") or "main"
    try:
        tree=get(f"https://api.github.com/repos/{USER}/{name}/git/trees/{branch}?recursive=1")
        entries=tree.get("tree",[])
        paths={x["path"] for x in entries if x["type"]=="blob"}
        truncated=tree.get("truncated",False)
    except Exception as e:
        return {"name":name,"status":"API_ERROR","details":str(e)[:180]}
    readme=next((p for p in paths if p.lower() in ("readme.md","readme.rst","readme.txt")),None)
    missing=[]
    candidates=[p for p in paths if "/" not in p and p.lower().endswith((".html",".htm",".md"))][:25]
    for path in candidates:
        try:
            raw=urllib.request.urlopen(urllib.request.Request(
                f"https://raw.githubusercontent.com/{USER}/{name}/{branch}/{urllib.parse.quote(path)}",
                headers={"User-Agent":HEADERS["User-Agent"]}),timeout=20).read().decode("utf-8","replace")
        except Exception: continue
        refs=re.findall(r"""(?:href|src)\s*=\s*["']([^"'#]+)["']""",raw,re.I)
        if path.lower().endswith(".md"):
            refs += re.findall(r"""\]\(([^)]+)\)""",raw)
        for ref in refs:
            ref=ref.strip()
            if not ref or ref.startswith(("http://","https://","mailto:","tel:","data:","javascript:")): continue
            ref=ref.split("#",1)[0].split("?",1)[0]
            if not ref: continue
            target=str(Path(path).parent / ref)
            if target not in paths and target.rstrip("/") not in {p.rstrip("/") for p in paths}:
                missing.append(f"{path} -> {ref}")
    return {"name":name,"url":repo["html_url"],"default_branch":branch,
            "description":repo.get("description") or "MISSING",
            "readme":"PRESENT" if readme else "MISSING",
            "root_files":sum(1 for p in paths if "/" not in p),
            "potential_missing_local_refs":sorted(set(missing))[:30],
            "truncated_tree":truncated}

def main():
    repos=api_repos()
    reports=[audit(r) for r in repos]
    lines=["# GBSBFORYOU Automated Repository Completeness Scan","",
           f"Generated (UTC): {datetime.now(timezone.utc):%Y-%m-%d %H:%M}",
           f"Public original repositories scanned: {len(reports)}","",
           "Automated heuristic scan only. Potential missing references require manual/browser confirmation. This report does not modify application code, create placeholder pages, merge repositories, or delete files.",
           "","## Summary",
           f"- Missing README: {sum(1 for x in reports if x.get('readme')=='MISSING')}",
           f"- Missing repository description: {sum(1 for x in reports if x.get('description')=='MISSING')}",
           f"- Repositories with potential missing local references: {sum(1 for x in reports if x.get('potential_missing_local_refs'))}",
           f"- API/tree errors: {sum(1 for x in reports if x.get('status')=='API_ERROR')}",
           "","## Repository findings",""]
    for x in reports:
        lines.append(f"### [{x['name']}]({x.get('url','')})")
        if x.get("status")=="API_ERROR":
            lines.append(f"- Scan error: {x['details']}")
        else:
            lines += [f"- README: {x['readme']}",f"- Description: {x['description']}",
                      f"- Root-level files: {x['root_files']}",f"- Tree truncated: {x['truncated_tree']}"]
            if x["potential_missing_local_refs"]:
                lines.append("- Potential missing local references:")
                lines += [f"  - {v}" for v in x["potential_missing_local_refs"]]
        lines.append("")
    Path("AUTO_COMPLETENESS_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
if __name__=="__main__":
    main()
