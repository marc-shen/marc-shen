#!/usr/bin/env python3
"""生成 README 中 <!--START_SECTION:waka--> 与 <!--END_SECTION:waka--> 之间的
ASCII 统计块。数据全部来自 GitHub GraphQL，不依赖 WakaTime。"""

import json
import os
import re
import sys
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


def repos_containing(n):
    return f"{n:,} repo" + ("" if n == 1 else "s")


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
query($login:String!) {
  user(login:$login) {
    createdAt
    repositories(ownerAffiliations:OWNER, privacy:PUBLIC) { totalCount }
    contributionsCollection { contributionCalendar { totalContributions } }
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
        languages(first:10, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name } }
        }
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
    profile = graphql(PROFILE_Q, login=USER)["user"]

    repos, cursor = [], None
    while True:
        page = graphql(REPOS_Q, login=USER, cursor=cursor)["user"]["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    hours, weekdays, languages, disk = Counter(), Counter(), Counter(), 0
    for repo in repos:
        disk += repo.get("diskUsage") or 0
        for edge in (repo.get("languages") or {}).get("edges", []):
            languages[edge["node"]["name"]] += 1
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

    return profile, disk, hours, weekdays, languages


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
        f"> \U0001f4dc {profile['repositories']['totalCount']} Public Repositories",
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
            render(languages.most_common(10), repos_containing),
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
