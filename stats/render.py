"""Draw the profile README and its charts from stats.json.

Run with: python3 -I stats/render.py
"""

import json
import math
import textwrap
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from html import escape
from pathlib import Path
from string import Template

STATS_DIR = Path(__file__).resolve().parent
REPO_ROOT = STATS_DIR.parent
STATS_FILE = STATS_DIR / "stats.json"
TEMPLATE_FILE = STATS_DIR / "readme-template.md"
README_FILE = REPO_ROOT / "README.md"
ASSETS_DIR = REPO_ROOT / "assets"
METHOD_URL = "https://github.com/snnbotchway/snnbotchway/blob/main/stats/README.md"

# Charts are drawn at CHART_WIDTH and shown at DISPLAY_WIDTH, which keeps the
# smallest label at about 11px on a 390px phone and modest on a desktop.
DISPLAY_WIDTH = 560
CHART_WIDTH = 760
PR_CHART_HEIGHT = 470
LINES_CHART_HEIGHT = 380
PAD = 16
EDGE = 4
BAR_SHARE = 0.68
LEGEND_Y = 30
AXIS_SPACE = 50
LABEL_SIZE = 26
VALUE_SIZE = 28
ROW_HEIGHT = 34
LABEL_GAP = 8
FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif'


class Theme(StrEnum):
    LIGHT = "light"
    DARK = "dark"


class Chart(StrEnum):
    PRS = "prs"
    LINES = "lines"


class Tone(StrEnum):
    INK = "ink"
    MUTED = "muted"


class Anchor(StrEnum):
    START = "start"
    MIDDLE = "middle"
    END = "end"


@dataclass(frozen=True)
class Palette:
    ink: str
    muted: str
    sizes: tuple[str, str, str, str]
    added: str
    deleted: str


PALETTES = {
    Theme.LIGHT: Palette("#1f2328", "#59636e", ("#86b6ef", "#3987e5", "#1c5cab", "#0d366b"), "#1a7f37", "#cf222e"),
    Theme.DARK: Palette("#f0f6fc", "#9198a1", ("#184f95", "#3987e5", "#86b6ef", "#cde2fb"), "#3fb950", "#f85149"),
}


def text_width(text: str, size: float, bold: bool = False) -> float:
    return len(text) * size * (0.6 if bold else 0.54)


def compact(n: int) -> str:
    if n >= 999_500:
        return f"{n / 1e6:.1f}M"
    return f"{round(n / 1000)}k" if n >= 1000 else str(n)


def ordinal(n: int) -> str:
    suffix = "th" if 10 < n % 100 < 14 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def month_start(key: str) -> date:
    return date.fromisoformat(f"{key}-01")


def balanced_rows(text: str, size: float, width: float, bold: bool) -> list[str]:
    """Wrap to the fewest rows that fit, then narrow the rows as far as that count allows."""
    chars = max(int(width / text_width("x", size, bold)), 1)
    rows = textwrap.wrap(text, chars, break_long_words=False)
    while chars > 1 and len(narrower := textwrap.wrap(text, chars - 1, break_long_words=False)) == len(rows):
        chars, rows = chars - 1, narrower
    return rows


def spaced(first: int, last: int, step: float, need: float) -> list[int]:
    """Indices from first to last, thinned so labels `need` wide never touch; last is always kept."""
    every = math.ceil(need / step)
    return list(range(first, last + 1, every))[:-1] + [last]


class Svg:
    def __init__(self, height: int, theme: Theme, label: str):
        self.height, self.palette, self.label, self.parts = height, PALETTES[theme], label, []

    def text(self, x, y, text, size, tone=Tone.INK, anchor=Anchor.START, bold=False):
        width = text_width(text, size, bold)
        left = {Anchor.START: x, Anchor.MIDDLE: x - width / 2, Anchor.END: x - width}[anchor]
        x += max(EDGE - left, 0) + min(CHART_WIDTH - EDGE - (left + width), 0)
        weight = ' font-weight="600"' if bold else ""
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" class="{tone}" '
                          f'text-anchor="{anchor}"{weight}>{escape(text)}</text>')

    def rows(self, x, y, rows, size, anchor, bold=False):
        for i, row in enumerate(rows):
            self.text(x, y + i * ROW_HEIGHT, row, size, Tone.INK, anchor, bold)

    def rect(self, x, y, width, height, fill, radius=2):
        if height > 0:
            self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
                              f'rx="{radius}" fill="{fill}"/>')

    def line(self, x1, y1, x2, y2, dash=""):
        dashes = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{self.palette.muted}" stroke-width="2"{dashes}/>')

    def legend(self, x, y, items):
        swatch = LABEL_SIZE * 0.75
        for color, name in items:
            self.rect(x, y - LABEL_SIZE * 0.72, swatch, swatch, color, 3)
            x += swatch + 6
            self.text(x, y, name, LABEL_SIZE, Tone.MUTED)
            x += text_width(name, LABEL_SIZE) + LABEL_SIZE * 0.8

    def render(self) -> str:
        p = self.palette
        style = f"text{{font-family:{FONT}}}.{Tone.INK}{{fill:{p.ink}}}.{Tone.MUTED}{{fill:{p.muted}}}"
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CHART_WIDTH} {self.height}" '
                f'width="{CHART_WIDTH}" height="{self.height}" role="img" aria-label="{escape(self.label)}">'
                f'<style>{style}</style>{"".join(self.parts)}</svg>\n')


@dataclass(frozen=True)
class Frame:
    """Shared geometry, so both charts line up month for month."""

    keys: list[str]
    surge: int

    @property
    def step(self) -> float:
        return (CHART_WIDTH - 2 * PAD) / len(self.keys)

    @property
    def bar(self) -> float:
        return self.step * BAR_SHARE

    @property
    def last(self) -> int:
        return len(self.keys) - 1

    def left(self, i: int) -> float:
        return PAD + self.step * i + (self.step - self.bar) / 2

    def centre(self, i: int) -> float:
        return self.left(i) + self.bar / 2

    @property
    def surge_x(self) -> float:
        return PAD + self.step * self.surge - 1

    def labelled(self, labels: list[str], size: float, bold: bool) -> list[int]:
        need = max(text_width(label, size, bold) for label in labels) + LABEL_GAP
        return spaced(self.surge, self.last, self.step, need)

    def beneath(self, i: int, width: float) -> range:
        """Indices of the bars a label of `width` centred over bar i would cross."""
        reach = math.floor((width / 2 + self.bar / 2) / self.step)
        return range(max(i - reach, 0), min(i + reach, self.last) + 1)


def draw_surge_line(svg: Svg, frame: Frame, top: float, bottom: float) -> None:
    svg.line(frame.surge_x, top, frame.surge_x, bottom, "6 6")


def draw_month_axis(svg: Svg, frame: Frame) -> None:
    y = svg.height - 12
    svg.text(frame.left(0), y, f"{month_start(frame.keys[0]):%b %Y}", LABEL_SIZE, Tone.MUTED)
    names = [f"{month:%b %Y}" if month.month == 1 else f"{month:%b}" for month in map(month_start, frame.keys)]
    for i in frame.labelled(names[frame.surge:], LABEL_SIZE, False):
        svg.text(frame.centre(i), y, names[i], LABEL_SIZE, Tone.MUTED, Anchor.MIDDLE)


def pr_chart(stats: dict, frame: Frame, theme: Theme) -> str:
    months = stats["months"]
    svg = Svg(PR_CHART_HEIGHT, theme, "Merged pull requests per month, stacked by size")
    title = "Lines per PR"
    svg.text(PAD, LEGEND_Y, title, LABEL_SIZE, Tone.MUTED)
    bands = stats["size_bands"]
    swatches = [(color, band["label"]) for color, band in zip(svg.palette.sizes, bands)]
    svg.legend(PAD + text_width(title, LABEL_SIZE) + 22, LEGEND_Y, swatches)

    plot_top, base = LEGEND_Y + 24, PR_CHART_HEIGHT - AXIS_SPACE
    scale = (base - plot_top - VALUE_SIZE - 12) / max(max(m["prs"] for m in months.values()), 1)
    tops = []
    for i, key in enumerate(frame.keys):
        y = base
        for color, band in zip(svg.palette.sizes, bands):
            segment = months[key][band["key"]] * scale
            gap = 2 if segment >= 6 and y != base else 0
            svg.rect(frame.left(i), y - segment, frame.bar, segment - gap, color)
            y -= segment
        tops.append(y)

    counts = [f"{months[key]['prs']:,}" for key in frame.keys]
    for i in frame.labelled(counts[frame.surge:], VALUE_SIZE, True):
        clear = min(tops[j] for j in frame.beneath(i, text_width(counts[i], VALUE_SIZE, True)))
        svg.text(frame.centre(i), clear - 10, counts[i], VALUE_SIZE, anchor=Anchor.MIDDLE, bold=True)

    before = f"about {round(stats['monthly_prs_before_surge'])} a month"
    span = frame.left(frame.surge - 1) + frame.bar - frame.left(0)
    rows = balanced_rows(before, VALUE_SIZE, span, False)
    svg.rows((frame.left(0) + frame.left(frame.surge - 1) + frame.bar) / 2,
             min(tops[:frame.surge]) - 16 - (len(rows) - 1) * ROW_HEIGHT, rows, VALUE_SIZE, Anchor.MIDDLE)

    draw_surge_line(svg, frame, plot_top, base)
    note = f"{month_start(stats['surge_month']):%b %Y}: built my agent fleet"
    note_x = frame.surge_x - 12
    svg.rows(note_x, plot_top + 26, balanced_rows(note, VALUE_SIZE, note_x - PAD, True), VALUE_SIZE, Anchor.END, True)
    svg.line(PAD, base + 1, CHART_WIDTH - PAD, base + 1)
    draw_month_axis(svg, frame)
    return svg.render()


def lines_chart(stats: dict, frame: Frame, theme: Theme) -> str:
    months = stats["months"]
    cap = f"capped at {stats['line_cap_per_pr']:,} lines per PR"
    svg = Svg(LINES_CHART_HEIGHT, theme, f"Lines added and deleted per month, {cap}")
    svg.legend(PAD, LEGEND_Y, [(svg.palette.added, "added"), (svg.palette.deleted, "deleted")])
    svg.text(CHART_WIDTH - PAD, LEGEND_Y, cap, LABEL_SIZE, Tone.MUTED, Anchor.END)

    plot_top, bottom = LEGEND_Y + 24, LINES_CHART_HEIGHT - AXIS_SPACE
    added = max(m["additions"] for m in months.values())
    deleted = max(m["deletions"] for m in months.values())
    scale = (bottom - plot_top - 2 * (VALUE_SIZE + 8)) / max(added + deleted, 1)
    base = plot_top + VALUE_SIZE + 8 + added * scale
    for i, key in enumerate(frame.keys):
        up, down = months[key]["additions"] * scale, months[key]["deletions"] * scale
        svg.rect(frame.left(i), base - up - 1, frame.bar, up, svg.palette.added)
        svg.rect(frame.left(i), base + 1, frame.bar, down, svg.palette.deleted)

    latest = months[frame.keys[-1]]
    up, down = latest["additions"] * scale, latest["deletions"] * scale
    x = frame.centre(frame.last)
    svg.text(x, base - up - 10, compact(latest["additions"]), VALUE_SIZE, anchor=Anchor.MIDDLE, bold=True)
    svg.text(x, base + down + VALUE_SIZE, compact(latest["deletions"]), VALUE_SIZE, anchor=Anchor.MIDDLE, bold=True)

    draw_surge_line(svg, frame, plot_top, bottom)
    draw_month_axis(svg, frame)
    return svg.render()


def picture(chart: Chart, alt: str) -> str:
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{chart}-{Theme.DARK}.svg">'
            f'<img src="assets/{chart}-{Theme.LIGHT}.svg" alt="{escape(alt)}" width="{DISPLAY_WIDTH}"></picture>')


def is_partial(month: date, generated: date) -> bool:
    """The month the stats were collected in is still in progress, even on its last day."""
    return (month.year, month.month) == (generated.year, generated.month)


def readme(stats: dict, frame: Frame) -> str:
    months, since = stats["months"], stats["since_surge"]
    generated = date.fromisoformat(stats["generated"])
    surge = month_start(stats["surge_month"])
    surge_name = f"{surge:%B}" if surge.year == generated.year else f"{surge:%B %Y}"
    latest = month_start(frame.keys[-1])
    partial = is_partial(latest, generated)
    prs_alt = (f"Merged PRs per month by size: about {round(stats['monthly_prs_before_surge'])} a month until "
               f"{month_start(frame.keys[frame.surge - 1]):%B %Y}, then {months[stats['surge_month']]['prs']} "
               f"in {surge:%B} and {months[frame.keys[-1]]['prs']} {'so far ' if partial else ''}in {latest:%B}")
    lines_alt = f"Lines added and deleted per month, capped at {stats['line_cap_per_pr']:,} lines per PR"
    return Template(TEMPLATE_FILE.read_text()).substitute(
        surge_month=surge_name,
        prs_chart=picture(Chart.PRS, prs_alt),
        lines_chart=picture(Chart.LINES, lines_alt),
        partial_month_note=f"{latest:%B} counts to the {ordinal(generated.day)}. " if partial else "",
        private=f"{since['private_prs']:,}",
        prs=f"{since['prs']:,}",
        repos=since["repos"],
        private_projects=since["private_projects"],
        median=f"{since['median']:,}",
        p90=f"{since['p90']:,}",
        tests=round(since["test_share"] * 100),
        written=compact(since["lines_written"]),
        over_1k=f"{since['over_1k']:,}",
        over_5k=f"{since['over_5k']:,}",
        updated=f"{generated.day} {generated:%b %Y}",
        method_url=METHOD_URL,
    )


def charted_months(stats: dict) -> list[str]:
    """Every month, but a month in progress only once it has overtaken the one before it.

    Otherwise the first week of each month draws a near-empty bar that reads as a collapse.
    """
    keys = sorted(stats["months"])
    latest, previous = keys[-1], keys[-2]
    in_progress = is_partial(month_start(latest), date.fromisoformat(stats["generated"]))
    if in_progress and stats["months"][latest]["prs"] < stats["months"][previous]["prs"]:
        return keys[:-1]
    return keys


def main() -> None:
    stats = json.loads(STATS_FILE.read_text())
    keys = charted_months(stats)
    frame = Frame(keys, keys.index(stats["surge_month"]))
    ASSETS_DIR.mkdir(exist_ok=True)
    for theme in Theme:
        (ASSETS_DIR / f"{Chart.PRS}-{theme}.svg").write_text(pr_chart(stats, frame, theme))
        (ASSETS_DIR / f"{Chart.LINES}-{theme}.svg").write_text(lines_chart(stats, frame, theme))
    README_FILE.write_text(readme(stats, frame))


if __name__ == "__main__":
    main()
