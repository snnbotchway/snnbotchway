"""Count merged PRs and the hand-written lines in them, and write aggregate totals only.

Per-PR data (repo names, titles, file paths) stays in the local cache; the
written stats.json holds monthly totals, so publishing it reveals no private work.
"""

import fnmatch
import json
import re
import statistics
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from enum import StrEnum
from pathlib import Path

USER = "snnbotchway"
FIRST_MONTH = date(2025, 11, 1)
SURGE_MONTH = "2026-09"
LINE_CAP_PER_PR = 5000
DATA_FILE_LINE_LIMIT = 500

CACHE_DIR = Path.home() / ".cache" / "profile-stats"
OUT_FILE = Path(__file__).resolve().parent / "stats.json"


class Size(StrEnum):
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"


SIZE_FLOORS = [(Size.XL, 5000), (Size.L, 1000), (Size.M, 100), (Size.S, 0)]

LOCKFILES = {
    "bun.lock", "bun.lockb", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "cargo.lock", "uv.lock", "poetry.lock", "pipfile.lock", "composer.lock",
    "gemfile.lock", "go.sum", "flake.lock", "foundry.lock",
}
GENERATED_DIRS = {
    "vendor", "node_modules", "dist", "build", "out", "artifacts", "broadcast",
    "typechain", "typechain-types", "generated", "__generated__",
    ".next", "coverage", "abis", "abi", "deployments", "snapshots",
    "__snapshots__", "migrations", "storybook-static",
}
GENERATED_SUFFIXES = (
    ".min.js", ".min.css", ".map", ".snap", ".gas-snapshot", ".svg", ".png",
    ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".ttf",
    ".otf", ".pdf", ".lock", ".generated.ts", ".gen.ts", "routeTree.gen.ts",
    ".pb.go", "_pb2.py", ".sql.go", "_gen.go", ".g.dart", ".freezed.dart",
)
GENERATED_NAME = re.compile(r"(^|[._-])(generated|autogen)([._-]|$)")
DATA_SUFFIXES = (".html", ".json", ".jsonl", ".csv", ".tsv", ".yaml", ".yml", ".xml", ".sql", ".parquet")
TEST_PATTERN = re.compile(
    r"(^|/)(tests?|__tests__|spec|e2e)/|(^|/)test_[^/]+$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$|\.t\.sol$"
)
PROMOTION_BRANCHES = {"main", "master", "staging", "develop", "dev", "production", "prod", "release"}
SKIPPED_TITLE = re.compile(
    r"^(revert\b|bump\b|(chore|build)\(deps|(back-?)?merge\b|update fork\b|((chore|build|ci)(\([^)]*\))?: )?promote\b)"
    r"|\bupstream\b",
    re.I,
)


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def read_cache(name: str):
    file = CACHE_DIR / name
    return json.loads(file.read_text()) if file.exists() else None


def write_cache(name: str, value) -> None:
    file = CACHE_DIR / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(value))


SEARCH_QUERY = """
query($q: String!, $endCursor: String) {
  search(query: $q, type: ISSUE, first: 100, after: $endCursor) {
    pageInfo { hasNextPage endCursor }
    nodes { ... on PullRequest {
      number title mergedAt baseRefName headRefName additions deletions
      repository { nameWithOwner isPrivate }
    } }
  }
}
"""


def month_starts(until: date):
    month = FIRST_MONTH
    while month <= until:
        yield month
        month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)


def merged_prs(today: date) -> list[dict]:
    """One search per month keeps each query under GitHub's 1,000-result search cap."""
    prs = []
    for start in month_starts(today):
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        query = f"author:{USER} is:pr is:merged merged:{start}..{end}"
        out = gh("api", "graphql", "--paginate", "-f", f"query={SEARCH_QUERY}", "-f", f"q={query}",
                 "--jq", ".data.search.nodes[]")
        prs += [json.loads(line) for line in out.splitlines() if line]
    return prs


def is_repeat_of_counted_work(pr: dict) -> bool:
    """Promotion PRs (staging -> main) and back-merges carry code already counted in feature PRs."""
    base, head = pr["baseRefName"].lower(), pr["headRefName"].lower()
    if base in PROMOTION_BRANCHES and head in PROMOTION_BRANCHES:
        return True
    return bool(SKIPPED_TITLE.search(pr["title"]))


def linguist_patterns(repo: str) -> list[str]:
    cached = read_cache(f"gitattributes/{repo.replace('/', '__')}.json")
    if cached is not None:
        return cached
    try:
        text = gh("api", f"repos/{repo}/contents/.gitattributes", "-H", "Accept: application/vnd.github.raw")
    except subprocess.CalledProcessError:
        text = ""
    patterns = [
        line.split()[0].lstrip("/")
        for line in text.splitlines()
        if re.search(r"linguist-(generated|vendored)(=true)?(\s|$)", line) and not line.startswith("#")
    ]
    write_cache(f"gitattributes/{repo.replace('/', '__')}.json", patterns)
    return patterns


def is_written_by_hand(path: str, changes: int, linguist: list[str]) -> bool:
    lower = path.lower()
    parts = lower.split("/")
    if parts[-1] in LOCKFILES or lower.endswith(GENERATED_SUFFIXES) or GENERATED_NAME.search(parts[-1]):
        return False
    if any(part in GENERATED_DIRS for part in parts[:-1]):
        return False
    if lower.endswith(DATA_SUFFIXES) and changes > DATA_FILE_LINE_LIMIT:
        return False
    return not any(fnmatch.fnmatch(path, p) or fnmatch.fnmatch(path, p.rstrip("/") + "/*") for p in linguist)


def pr_files(pr: dict) -> list[list]:
    """[path, additions, deletions] for each file of a merged PR; cached, since merged PRs do not change."""
    repo, number = pr["repository"]["nameWithOwner"], pr["number"]
    key = f"files/{repo.replace('/', '__')}__{number}.json"
    cached = read_cache(key)
    if cached is not None:
        return cached
    out = gh("api", "--paginate", f"repos/{repo}/pulls/{number}/files?per_page=100",
             "--jq", ".[] | [.filename, .additions, .deletions] | @json")
    files = [json.loads(row) for row in out.splitlines()]
    write_cache(key, files)
    return files


def pr_lines(pr: dict) -> dict:
    linguist = linguist_patterns(pr["repository"]["nameWithOwner"])
    lines = {"additions": 0, "deletions": 0, "tests": 0}
    for path, additions, deletions in pr_files(pr):
        if not is_written_by_hand(path, additions + deletions, linguist):
            continue
        lines["additions"] += additions
        lines["deletions"] += deletions
        if TEST_PATTERN.search(path.lower()):
            lines["tests"] += additions + deletions
    return lines


def size_of(lines: int) -> Size:
    return next(size for size, floor in SIZE_FLOORS if lines >= floor)


def capped(lines: dict) -> tuple[int, int]:
    total = lines["additions"] + lines["deletions"]
    if total <= LINE_CAP_PER_PR:
        return lines["additions"], lines["deletions"]
    scale = LINE_CAP_PER_PR / total
    return round(lines["additions"] * scale), round(lines["deletions"] * scale)


def summarize(rows: list[dict], skipped: int, today: date) -> dict:
    months = {
        m.strftime("%Y-%m"): {"prs": 0, "private": 0, "additions": 0, "deletions": 0, **{s.value: 0 for s in Size}}
        for m in month_starts(today)
    }
    for row in rows:
        month = months[row["month"]]
        month["prs"] += 1
        month["private"] += row["private"]
        month[size_of(row["total"]).value] += 1
        additions, deletions = capped(row)
        month["additions"] += additions
        month["deletions"] += deletions

    def window(since: date) -> dict:
        picked = [r for r in rows if r["merged"] >= since]
        totals = sorted(r["total"] for r in picked)
        written = sum(totals)
        return {
            "prs": len(picked),
            "repos": len({r["repo"] for r in picked}),
            "private_repos": len({r["repo"] for r in picked if r["private"]}),
            "over_1k": sum(t >= 1000 for t in totals),
            "over_5k": sum(t >= 5000 for t in totals),
            "median": round(statistics.median(totals)) if totals else 0,
            "p90": totals[int(len(totals) * 0.9)] if totals else 0,
            "lines_written": written,
            "lines_counted": sum(sum(capped(r)) for r in picked),
            "test_share": round(sum(r["tests"] for r in picked) / written, 3) if written else 0,
        }

    before = [m for key, m in months.items() if key < SURGE_MONTH]
    return {
        "generated": today.isoformat(),
        "surge_month": SURGE_MONTH,
        "line_cap_per_pr": LINE_CAP_PER_PR,
        "months": months,
        "last_30_days": window(today - timedelta(days=30)),
        "since_surge": window(date.fromisoformat(f"{SURGE_MONTH}-01")),
        "monthly_prs_before_surge": round(sum(m["prs"] for m in before) / len(before), 1),
        "skipped_repeat_prs": skipped,
    }


def main() -> None:
    today = datetime.now(UTC).date()
    rows = []
    skipped = 0
    for pr in merged_prs(today):
        if is_repeat_of_counted_work(pr):
            skipped += 1
            continue
        lines = pr_lines(pr)
        rows.append({
            "month": pr["mergedAt"][:7],
            "merged": date.fromisoformat(pr["mergedAt"][:10]),
            "repo": pr["repository"]["nameWithOwner"],
            "private": int(pr["repository"]["isPrivate"]),
            "total": lines["additions"] + lines["deletions"],
            **lines,
        })
    stats = summarize(rows, skipped, today)
    OUT_FILE.write_text(json.dumps(stats, indent=2) + "\n")
    print(f"{len(rows)} PRs counted, {skipped} skipped as repeats", file=sys.stderr)


if __name__ == "__main__":
    main()
