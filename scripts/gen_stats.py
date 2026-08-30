#!/usr/bin/env python3
"""生成 README 中 <!--START_SECTION:waka--> 与 <!--END_SECTION:waka--> 之间的
ASCII 统计块。数据全部来自 GitHub GraphQL，不依赖 WakaTime。"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

API = "https://api.github.com/graphql"
TOKEN = os.environ["GH_TOKEN"]
USER = os.environ.get("GH_USER", "marc-shen")
TZ = timezone(timedelta(hours=int(os.environ.get("UTC_OFFSET", "8"))))

BAR_LEN = 25
FULL, EMPTY = "█", "░"


def graphql(query, **variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": USER,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def bar(fraction):
    filled = round(fraction * BAR_LEN)
    return FULL * filled + EMPTY * (BAR_LEN - filled)


def lines_of_code(n):
    return f"{n:,} line" + ("" if n == 1 else "s")


# cloc 把同一门语言拆得很细，合并成一般人认得的名字
LANG_ALIASES = {
    "Bourne Shell": "Shell",
    "Bourne Again Shell": "Shell",
    "Fortran 77": "Fortran",
    "Fortran 90": "Fortran",
    "Fortran 95": "Fortran",
    "Lisp": "Emacs Lisp",
    "C++": "C++",
}

# 计入行数时忽略的非代码格式
SKIP_LANGS = "JSON,YAML,SVG,Markdown,Text,TOML,INI,XML,CSV,HTML"


def loc_by_language(names):
    """浅克隆每个仓库并用 cloc 统计各语言实际代码行数。

    cloc 原生支持 .ipynb，只数代码单元，不会把 base64 输出图算成代码。
    """
    cloc = os.environ.get("CLOC", "cloc")
    counts = Counter()
    workdir = tempfile.mkdtemp(prefix="loc-")
    try:
        for name in names:
            target = os.path.join(workdir, name)
            clone = subprocess.run(
                ["git", "clone", "--quiet", "--depth", "1", "--single-branch",
                 f"https://github.com/{USER}/{name}.git", target],
                capture_output=True,
            )
            if clone.returncode != 0:
                print(f"skip {name}: clone failed", file=sys.stderr)
                continue

        command = [cloc, "--json", "--quiet",
                   "--exclude-dir=node_modules,vendor,dist,build",
                   f"--exclude-lang={SKIP_LANGS}", workdir]
        if cloc.endswith(".pl"):
            command.insert(0, "perl")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            print(f"cloc failed: {result.stderr[:400]}", file=sys.stderr)
            return counts
        for language, stats in json.loads(result.stdout).items():
            if language in ("header", "SUM"):
                continue
            counts[LANG_ALIASES.get(language, language)] += stats["code"]
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return counts


def render(rows, describe):
    """rows: [(label, value)] -> anmol098 风格的等宽条形图。"""
    total = sum(v for _, v in rows) or 1
    out = []
    for label, value in rows:
        frac = value / total
        out.append(
            f"{label:<25}{describe(value):<20}{bar(frac)}   {frac * 100:05.2f} % "
        )
    return "\n".join(out)


def commits(n):
    return f"{n:,} commit" + ("" if n == 1 else "s")


PROFILE_Q = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    createdAt
    repositories(ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false) { totalCount }
    contributionsCollection(from:$from, to:$to) {
      contributionCalendar { totalContributions }
    }
  }
}
"""

REPOS_Q = """
query($login:String!, $cursor:String) {
  user(login:$login) {
    repositories(first:50, after:$cursor, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        diskUsage
        defaultBranchRef {
          target {
            ... on Commit {
              history(first:100) {
                nodes { committedDate author { user { login } } }
              }
            }
          }
        }
      }
    }
  }
}
"""


def collect():
    now = datetime.now(timezone.utc)
    year_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    profile = graphql(
        PROFILE_Q,
        login=USER,
        **{"from": year_start.isoformat(), "to": now.isoformat()},
    )["user"]

    repos, cursor = [], None
    while True:
        page = graphql(REPOS_Q, login=USER, cursor=cursor)["user"]["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    hours, weekdays, disk, names = Counter(), Counter(), 0, []
    for repo in repos:
        disk += repo.get("diskUsage") or 0
        names.append(repo["name"])
        ref = repo.get("defaultBranchRef") or {}
        target = ref.get("target") or {}
        for commit in (target.get("history") or {}).get("nodes", []):
            user = (commit.get("author") or {}).get("user") or {}
            if user.get("login", "").lower() != USER.lower():
                continue
            when = datetime.fromisoformat(
                commit["committedDate"].replace("Z", "+00:00")
            ).astimezone(TZ)
            hours[when.hour] += 1
            weekdays[when.strftime("%A")] += 1

    return profile, disk, hours, weekdays, loc_by_language(names)


def build(profile, disk, hours, weekdays, languages):
    joined = datetime.fromisoformat(profile["createdAt"].replace("Z", "+00:00"))
    years = max(1, int((datetime.now(timezone.utc) - joined).days / 365.25))
    contributions = profile["contributionsCollection"]["contributionCalendar"][
        "totalContributions"
    ]

    blocks = [
        "**\U0001f431 My GitHub Data**",
        "",
        f"> \U0001f4e6 {disk / 1000:,.1f} MB Used in GitHub's Storage",
        "> ",
        f"> \U0001f3c6 {contributions:,} Contributions in the Year "
        f"{datetime.now(TZ).year}",
        "> ",
        f"> \U0001f4dc {profile['repositories']['totalCount']} Public Repositories (excluding forks)",
        "> ",
        f"> \U0001f5d3️ Joined GitHub {years} years ago",
        "",
    ]

    buckets = [
        ("\U0001f31e Morning", range(6, 12)),
        ("\U0001f306 Daytime", range(12, 18)),
        ("\U0001f303 Evening", range(18, 24)),
        ("\U0001f319 Night", list(range(0, 6))),
    ]
    by_bucket = [(name, sum(hours[h] for h in span)) for name, span in buckets]
    peak = max(by_bucket, key=lambda kv: kv[1])[0] if any(hours.values()) else ""
    owl = "I'm a Night \U0001f989" if "Night" in peak or "Evening" in peak else "I'm an Early \U0001f424"
    blocks += [f"**{owl}**", "", "```text", render(by_bucket, commits), "```", ""]

    order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
    ]
    if weekdays:
        best = max(order, key=lambda d: weekdays[d])
        blocks += [
            f"\U0001f4c5 **I'm Most Productive on {best}**",
            "",
            "```text",
            render([(d, weekdays[d]) for d in order], commits),
            "```",
            "",
        ]

    if languages:
        top = languages.most_common(1)[0][0]
        blocks += [
            f"**I Mostly Code in {top}**",
            "",
            "```text",
            render(languages.most_common(10), lines_of_code),
            "```",
            "",
        ]

    stamp = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")
    blocks.append(f" Last Updated on {stamp}")
    return "\n".join(blocks)


def main():
    section = build(*collect())
    path = os.environ.get("README_PATH", "README.md")
    with open(path, encoding="utf-8") as f:
        readme = f.read()

    pattern = re.compile(
        r"(<!--START_SECTION:waka-->).*?(<!--END_SECTION:waka-->)", re.DOTALL
    )
    if not pattern.search(readme):
        sys.exit("README 中找不到 waka section 标记")

    updated = pattern.sub(lambda m: f"{m.group(1)}\n\n{section}\n\n{m.group(2)}", readme)
    if updated == readme:
        print("no change")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    print("updated")


if __name__ == "__main__":
    main()
