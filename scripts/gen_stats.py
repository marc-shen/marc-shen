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
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

API = "https://api.github.com/graphql"
TOKEN = os.environ["GH_TOKEN"]
USER = os.environ.get("GH_USER", "marc-shen")
TZ = timezone(timedelta(hours=int(os.environ.get("UTC_OFFSET", "8"))))

# 网页/静态站项目：算的是模板和样式，不代表日常写的代码
EXCLUDE_REPOS = {
    name.strip()
    for name in os.environ.get("EXCLUDE_REPOS", "Dream-Quest").split(",")
    if name.strip()
}

# fork 默认不计，但自己在上面持续开发的除外
INCLUDE_FORKS = {
    name.strip()
    for name in os.environ.get("INCLUDE_FORKS", "EMPi").split(",")
    if name.strip()
}

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
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                payload = json.load(r)
            break
        except urllib.error.HTTPError as err:
            # 5xx 多为偶发，退避后重试；4xx 直接抛出
            if err.code < 500 or attempt == 3:
                raise
            time.sleep(2 ** attempt)
        except urllib.error.URLError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
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
# 数据/标记格式与 notebook 不计入代码行数
SKIP_LANGS = ",".join([
    # 数据与标记格式
    "JSON", "YAML", "SVG", "Markdown", "Text", "TOML", "INI", "XML", "CSV",
    "reStructuredText", "TeX", "SQL Data", "Diff", "VSCode Workspace",
    "Windows Resource File",
    # notebook（字节数量的是输出图，不是代码）
    "Jupyter Notebook",
    # 网页与前端
    "HTML", "CSS", "SCSS", "Sass", "LESS", "Stylus", "JavaScript", "JSX",
    "TypeScript", "TSX", "Vuejs Component", "Svelte", "Astro", "Handlebars",
    "Pug", "Twig", "EJS", "Liquid",
])

# 构建产物、依赖、文档生成目录里的代码不是自己写的
EXCLUDE_DIRS = ",".join([
    "node_modules", "vendor", "dist", "build", "_build", "_static",
    "site-packages", ".venv", "venv", "third_party", "external",
    "egg-info", ".eggs",
])


def loc_by_language(names):
    """浅克隆每个仓库并用 cloc 统计各语言实际代码行数。

    cloc 原生支持 .ipynb，只数代码单元，不会把 base64 输出图算成代码。
    """
    cloc = os.environ.get("CLOC", "cloc")
    counts, failed = Counter(), []
    workdir = tempfile.mkdtemp(prefix="loc-")
    try:
        for name in names:
            target = os.path.join(workdir, name)
            for attempt in range(3):
                clone = subprocess.run(
                    ["git", "clone", "--quiet", "--depth", "1", "--single-branch",
                     f"https://x-access-token:{TOKEN}@github.com/{USER}/{name}.git",
                     target],
                    capture_output=True, text=True,
                )
                if clone.returncode == 0:
                    break
                shutil.rmtree(target, ignore_errors=True)
                time.sleep(2 * (attempt + 1))
            else:
                # 静默跳过会让统计结果悄悄失真，宁可让这次运行显式失败
                failed.append(f"{name}: {clone.stderr.strip()[:200]}")
                continue
            time.sleep(1)

        if failed:
            raise RuntimeError("无法克隆以下仓库:\n  " + "\n  ".join(failed))

        command = [cloc, "--json", "--quiet",
                   "--exclude-dir=" + EXCLUDE_DIRS,
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
    repositories(first:50, after:$cursor, ownerAffiliations:OWNER) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        isFork
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
        name = repo["name"]
        if repo.get("isFork") and name not in INCLUDE_FORKS:
            continue
        disk += repo.get("diskUsage") or 0
        names.append(name)
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

    counted = [n for n in names if n not in EXCLUDE_REPOS]
    return profile, disk, hours, weekdays, loc_by_language(counted)


def build(profile, disk, hours, weekdays, languages):
    """整段输出是一个仿 shell 会话，与 README 其余章节风格一致。"""
    joined = datetime.fromisoformat(profile["createdAt"].replace("Z", "+00:00"))
    years = max(1, int((datetime.now(timezone.utc) - joined).days / 365.25))
    contributions = profile["contributionsCollection"]["contributionCalendar"][
        "totalContributions"
    ]
    year = datetime.now(TZ).year

    lines = [
        "```console",
        "marc@bnu:~$ gh-stats --summary",
        f"storage        {disk / 1000:,.1f} MB",
        f"contributions  {contributions:,} in {year}",
        f"public repos   {profile['repositories']['totalCount']} (forks excluded)",
        f"member since   {joined.year} ({years} years)",
        "",
    ]

    buckets = [
        ("\U0001f31e Morning", range(6, 12)),
        ("\U0001f306 Daytime", range(12, 18)),
        ("\U0001f303 Evening", range(18, 24)),
        ("\U0001f319 Night", list(range(0, 6))),
    ]
    by_bucket = [(name, sum(hours[h] for h in span)) for name, span in buckets]
    lines += [
        "marc@bnu:~$ gh-stats --commits --group-by=daypart",
        render(by_bucket, commits),
        "",
    ]

    order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
    ]
    if weekdays:
        lines += [
            "marc@bnu:~$ gh-stats --commits --group-by=weekday",
            render([(d, weekdays[d]) for d in order], commits),
            "",
        ]

    if languages:
        lines += [
            "marc@bnu:~$ cloc --no-web --no-notebooks ~/src",
            render(languages.most_common(10), lines_of_code),
            "",
        ]

    stamp = datetime.now(timezone.utc).strftime("%a %b %d %H:%M:%S UTC %Y")
    lines += ["marc@bnu:~$ date -u", stamp, "```"]
    return "\n".join(lines)


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
