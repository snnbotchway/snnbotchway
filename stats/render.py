"""Draw the profile README and its charts from stats.json.

Run with: python3 -I stats/render.py
"""

import json
import math
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

# Charts are drawn at CHART_WIDTH and shown at DISPLAY_WIDTH. A 390px phone shrinks them to about 324px,
# so the smallest text (LABEL_SIZE) still renders at 11px there.
CHART_WIDTH = 560
DISPLAY_WIDTH = CHART_WIDTH
PAD = 16
EDGE = 4
LABEL_SIZE = 19
TOTAL_SIZE = 20
TITLE_SIZE = 22
LINE_HEIGHT = 1.3
LABEL_GAP = 8
TITLE_Y = 22  # title baseline; the unit line sits under it
UNIT_Y = 48
PLOT_TOP = 92  # the top gridline
PR_PLOT_HEIGHT = 262
LINES_PLOT_HEIGHT = 190
AXIS_GAP = 28  # plot floor to month label baseline
TOTALS_GAP = 26  # month label baseline to monthly total baseline
BAR_SHARE = 0.56  # of each month's slot, the rest is space between months
SEGMENT_GAP = 2  # page-coloured gap between stacked bands, so every boundary reads
MIN_BAR = 3  # a band with any PRs never draws a segment shorter than this, gap included
RADIUS = 2
LEADER = 16  # leader lines from the latest month to its direct labels
DOT = 4.5
SUMMARY_GAP = 12  # the lines chart opens a <details>, whose summary leaves no space under it
FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif'


class Theme(StrEnum):
    LIGHT = "light"
    DARK = "dark"


class Chart(StrEnum):
    PRS = "prs"
    LINES = "lines"


class Anchor(StrEnum):
    START = "start"
    MIDDLE = "middle"
    END = "end"


@dataclass(frozen=True)
class Palette:
    ink: str
    muted: str
    page: str
    grid: str
    rule: str
    # Size bands, smallest first, as one terracotta ramp: the biggest PRs get the most contrast.
    sizes: tuple[str, str, str, str]
    size_text: tuple[str, str, str, str]  # the same ramp, held to 4.5:1 for the direct labels
    added: str
    deleted: str


PALETTES = {
    Theme.LIGHT: Palette("#1f1c19", "#665f58", "#ffffff", "#e8e4df", "#b8afa6",
                         ("#dda184", "#cd7a58", "#a9512f", "#74301b"),
                         ("#a65a3d", "#a04f31", "#8f4329", "#74301b"), "#24773f", "#b5532f"),
    Theme.DARK: Palette("#efebe7", "#a39c95", "#0d1117", "#2a2928", "#57524d",
                        ("#874a35", "#b3654a", "#da8b6c", "#f3bea6"),
                        ("#c97a5e", "#d0866a", "#da8b6c", "#f3bea6"), "#5fc68a", "#e08463"),
}


def text_width(text: str, size: float, bold: bool = False) -> float:
    """Rough width in the system font stack; Noto Sans, the widest member, sets the factors."""
    em = sum(0.27 if ch == " " else 0.32 if ch in "ilI.,:;|'()[]1" else 0.85 if ch in "mwMW–"
             else 0.62 if ch.isupper() or ch.isdigit() else 0.55 for ch in text)
    return em * size * (1.02 if bold else 1)


def compact(n: int) -> str:
    if n >= 999_500:
        return f"{n / 1e6:.1f}M"
    return f"{round(n / 1000)}k" if n >= 1000 else str(n)


def tick_label(n: int) -> str:
    """A gridline value, exact: steps of 2.5 must not round."""
    return f"{n / 1e6:g}M" if n >= 1_000_000 else f"{n / 1000:g}k" if n >= 1000 else str(n)


def ticks(highest: int) -> list[int]:
    """Three to five round gridline values from 0 up past `highest`."""
    raw = max(highest, 1) / 4
    magnitude = 10 ** math.floor(math.log10(raw))
    step = max(1, next(m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw))
    return [round(step * i) for i in range(math.ceil(max(highest, 1) / step) + 1)]


def month_start(key: str) -> date:
    return date.fromisoformat(f"{key}-01")


def units(phrases: list[str], size: float, width: float, bold: bool) -> list[str]:
    """The phrases, except one too wide for a row of its own breaks into words."""
    return [word for phrase in phrases
            for word in ([phrase] if text_width(phrase, size, bold) <= width else phrase.split())]


def filled(pieces: list[str], size: float, width: float, bold: bool) -> list[str]:
    """Fill rows piece by piece."""
    rows: list[str] = []
    for piece in pieces:
        if rows and text_width(f"{rows[-1]} {piece}", size, bold) <= width:
            rows[-1] += f" {piece}"
        else:
            rows.append(piece)
    return rows


def balanced_rows(phrases: list[str], size: float, width: float, bold: bool) -> list[str]:
    """Wrap to the fewest rows that fit, then narrow the rows as far as that count allows,
    breaking only the phrases that never fit `width`."""
    pieces = units(phrases, size, width, bold)
    rows = filled(pieces, size, width, bold)
    while True:
        narrower = filled(pieces, size, max(text_width(row, size, bold) for row in rows) - 1, bold)
        if len(narrower) != len(rows) or narrower == rows:
            return rows
        rows = narrower


def spaced(first: int, last: int, step: float, need: float) -> list[int]:
    """Indices from first to last, thinned so labels `need` wide never touch; last is always kept."""
    every = math.ceil(need / step)
    return list(range(first, last + 1, every))[:-1] + [last]


def spread(wanted: list[float], gap: float, low: float, high: float) -> list[float]:
    """Move labels (sorted top to bottom) apart by at least `gap`, as little as possible, within low..high."""
    def clash(top: list[float], bottom: list[float]) -> bool:
        return sum(top) / len(top) + len(top) * gap / 2 > sum(bottom) / len(bottom) - len(bottom) * gap / 2

    groups: list[list[float]] = []  # runs of touching labels, each centred on the mean of where they want to be
    for y in wanted:
        groups.append([y])
        while len(groups) > 1 and clash(groups[-2], groups[-1]):
            groups[-2:] = [groups[-2] + groups[-1]]
    ys = [sum(g) / len(g) + (i - (len(g) - 1) / 2) * gap for g in groups for i in range(len(g))]
    for i, y in enumerate(ys):
        ys[i] = max(y, low if i == 0 else ys[i - 1] + gap)
    for i in reversed(range(len(ys))):
        ys[i] = min(ys[i], high if i == len(ys) - 1 else ys[i + 1] - gap)
    return ys


def bar_path(x: float, y: float, width: float, height: float, round_top: bool) -> str:
    """A bar segment, the top one with its top corners rounded."""
    r = min(RADIUS, width / 2, height) if round_top else 0
    return (f"M{x:.1f},{y + height:.1f}V{y + r:.1f}Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f}H{x + width - r:.1f}"
            f"Q{x + width:.1f},{y:.1f} {x + width:.1f},{y + r:.1f}V{y + height:.1f}Z")


def row_height(size: float) -> float:
    return size * LINE_HEIGHT


class Svg:
    def __init__(self, height: float, theme: Theme, label: str, margin: int = 0):
        """`margin` is clear space above the chart, for a chart that follows a line with no gap of its own."""
        self.height, self.palette, self.label, self.parts = math.ceil(height), PALETTES[theme], label, []
        self.margin = margin

    def text(self, x, y, text, size=LABEL_SIZE, fill="", anchor=Anchor.START, bold=False, halo=False):
        """`halo` rings the text in the page colour, so it reads over gridlines and leaders."""
        width = text_width(text, size, bold)
        left = {Anchor.START: x, Anchor.MIDDLE: x - width / 2, Anchor.END: x - width}[anchor]
        x += max(EDGE - left, 0) + min(CHART_WIDTH - EDGE - (left + width), 0)
        extra = (' font-weight="600"' if bold else "") + (
            f' stroke="{self.palette.page}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
            if halo else "")
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.palette.muted}" '
                          f'text-anchor="{anchor}"{extra}>{escape(text)}</text>')

    def rows(self, x, y, rows, size, fill, anchor, bold=False):
        for i, row in enumerate(rows):
            self.text(x, y + i * row_height(size), row, size, fill, anchor, bold, True)

    def path(self, d, fill="none", stroke="", width=1.0, dash=""):
        strokes = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        dashes = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<path d="{d}" fill="{fill}"{strokes}{dashes} stroke-linecap="round" '
                          f'stroke-linejoin="round"/>')

    def line(self, x1, y1, x2, y2, stroke, dash=""):
        self.path(f"M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}", stroke=stroke, dash=dash)

    def dot(self, x, y, fill):
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{DOT}" fill="{fill}" '
                          f'stroke="{self.palette.page}" stroke-width="2"/>')

    def heading(self, title: str, unit: str, note: str) -> None:
        """Title and unit line top left, a qualifier (the partial month) top right."""
        p = self.palette
        self.text(PAD, TITLE_Y, title, TITLE_SIZE, p.ink, bold=True)
        self.text(PAD, UNIT_Y, unit)
        if note:
            self.text(CHART_WIDTH - PAD, TITLE_Y, note, anchor=Anchor.END)

    def render(self) -> str:
        style = f"text{{font-family:{FONT};font-variant-numeric:tabular-nums}}"
        height = self.height + self.margin
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CHART_WIDTH} {height}" '
                f'width="{CHART_WIDTH}" height="{height}" role="img" aria-label="{escape(self.label)}">'
                f'<style>{style}</style><g transform="translate(0 {self.margin})">{"".join(self.parts)}</g></svg>\n')


@dataclass(frozen=True)
class Frame:
    """Shared geometry, so both charts line up month for month."""

    keys: list[str]
    surge: int
    left: float  # the plot's left edge, right of the gridline values
    gutter: float  # room right of the plot for the direct labels

    @property
    def right(self) -> float:
        return CHART_WIDTH - PAD - self.gutter

    @property
    def step(self) -> float:
        return (self.right - self.left) / len(self.keys)

    @property
    def last(self) -> int:
        return len(self.keys) - 1

    def centre(self, i: int) -> float:
        return self.left + self.step * (i + 0.5)

    @property
    def bar(self) -> float:
        return self.step * BAR_SHARE

    def bar_left(self, i: int) -> float:
        return self.centre(i) - self.bar / 2

    @property
    def surge_x(self) -> float:
        return self.left + self.step * self.surge

    def labelled(self, need: float) -> list[int]:
        return spaced(0, self.last, self.step, need + LABEL_GAP)


def draw_grid(svg: Svg, frame: Frame, values: list[int], base: float, scale: float) -> None:
    """Dashed gridlines at round values, labelled at the left; the floor is solid."""
    for value in values:
        y = base - value * scale
        if value:
            svg.line(frame.left, y, CHART_WIDTH - PAD, y, svg.palette.grid, "2 6")
        svg.text(frame.left - 10, y + LABEL_SIZE * 0.35, tick_label(value), anchor=Anchor.END)
    svg.line(frame.left, base, CHART_WIDTH - PAD, base, svg.palette.rule)


def draw_direct_labels(svg: Svg, frame: Frame, anchors: list[tuple[float, float]], labels: list[list[str]],
                       colors: list[str], bold_first: bool, low: float, high: float) -> None:
    """Name each series right of the plot in its own colour, with a leader from (x, y) on the latest month."""
    height = [row_height(LABEL_SIZE) * len(rows) for rows in labels]
    order = sorted(range(len(labels)), key=lambda j: anchors[j][1])
    ys = spread([anchors[j][1] for j in order], max(height), low, high)
    column = frame.right + LEADER
    for j, y in zip(order, ys):
        x, at = anchors[j]
        svg.path(f"M{x:.1f},{at:.1f}H{x + 4:.1f}L{column - 5:.1f},{y:.1f}", stroke=svg.palette.rule)
        first = y + LABEL_SIZE * 0.35 - (len(labels[j]) - 1) * row_height(LABEL_SIZE) / 2
        for k, row in enumerate(labels[j]):
            svg.text(column, first + k * row_height(LABEL_SIZE), row, fill=colors[j], bold=bold_first and k == 0)


def draw_month_axis(svg: Svg, frame: Frame, base: float, totals: list[str] | None = None) -> None:
    """Month names under the plot, and under each its total, the way a table would."""
    names = [f"{month_start(key):%b}" for key in frame.keys]
    need = max(*(text_width(name, LABEL_SIZE) for name in names),
               *(text_width(total, TOTAL_SIZE, True) for total in totals or []))
    for i in frame.labelled(need):  # one set of months for both rows, so a total never loses its name
        svg.text(frame.centre(i), base + AXIS_GAP, names[i], anchor=Anchor.MIDDLE)
        if totals:
            svg.text(frame.centre(i), base + AXIS_GAP + TOTALS_GAP, totals[i], TOTAL_SIZE, svg.palette.ink,
                     Anchor.MIDDLE, True)


def counted_to(stats: dict, frame: Frame) -> str:
    generated, latest = date.fromisoformat(stats["generated"]), month_start(frame.keys[-1])
    return f"counted to {latest:%b} {generated.day}" if is_partial(latest, generated) else ""


def surge_note(svg: Svg, frame: Frame, stats: dict, tops: list[float], base: float) -> None:
    """The surge note and its divider. The note takes the first spot, in the fewest rows, that clears every
    bar under it: beside the divider on the right, then on the left, then from the plot's left edge with the
    divider starting below it."""
    p, rh = svg.palette, row_height(LABEL_SIZE)
    surge = month_start(stats["surge_month"])
    words = [f"{surge:%b %Y}:", *"started building my agent workflow".split()]
    first = PLOT_TOP + 6
    spots = [(frame.surge_x + 12, Anchor.START), (frame.surge_x - 12, Anchor.END), (frame.left, Anchor.START)]

    def placed(rows: list[str], x: float, anchor: Anchor) -> tuple[float, float, float] | None:
        width = max(text_width(row, LABEL_SIZE, True) for row in rows)
        left = x if anchor == Anchor.START else x - width
        bottom = first + (len(rows) - 1) * rh + LABEL_SIZE * 0.3
        if left < frame.left - 1 or left + width > CHART_WIDTH - PAD:
            return None
        under = [tops[i] for i in range(len(tops))
                 if frame.bar_left(i) < left + width and frame.bar_left(i) + frame.bar > left]
        return (left, width, bottom) if all(top > bottom + 10 for top in under) else None

    choice = None
    for count in (2, 3, 4):
        for x, anchor in spots:
            for width in range(120, 340, 4):
                rows = balanced_rows(words, LABEL_SIZE, width, True)
                if len(rows) == count and placed(rows, x, anchor):
                    choice = rows, x, anchor
                    break
            if choice:
                break
        if choice:
            break
    rows, x, anchor = choice or (balanced_rows(words, LABEL_SIZE, 200, True), frame.left, Anchor.START)
    left, width, bottom = placed(rows, x, anchor) or (x, 0, first + (len(rows) - 1) * rh)
    crosses = left < frame.surge_x < left + width
    svg.line(frame.surge_x, bottom + 10 if crosses else first - LABEL_SIZE * 0.8, frame.surge_x, base, p.rule, "3 4")
    svg.rows(x, first, rows, LABEL_SIZE, p.ink, anchor, True)


def pr_chart(stats: dict, frame: Frame, theme: Theme) -> str:
    months, bands = stats["months"], stats["size_bands"]
    base = PLOT_TOP + PR_PLOT_HEIGHT
    first = month_start(frame.keys[0])
    svg = Svg(base + AXIS_GAP + TOTALS_GAP + 8, theme,
              f"Merged pull requests per month since {first:%B %Y}, stacked by lines per PR")
    p = svg.palette
    svg.heading("Merged PRs per month", "stacked by lines changed per PR", counted_to(stats, frame))
    values = ticks(max(months[key]["prs"] for key in frame.keys))
    scale = PR_PLOT_HEIGHT / values[-1]
    draw_grid(svg, frame, values, base, scale)

    # Bands stack smallest first from the floor; each segment above another gives up its bottom SEGMENT_GAP.
    tops, middles = [], []
    for i, key in enumerate(frame.keys):
        heights = [max(months[key][band["key"]] * scale, MIN_BAR) if months[key][band["key"]] else 0
                   for band in bands]
        highest = max((j for j, height in enumerate(heights) if height), default=-1)
        y, middles = base, []
        for j, height in enumerate(heights):
            gap = SEGMENT_GAP if height and y < base else 0
            if height:
                svg.path(bar_path(frame.bar_left(i), y - height, frame.bar, height - gap, j == highest), p.sizes[j])
            middles.append(y - (height + gap) / 2)
            y -= height
        tops.append(y)
    right = frame.bar_left(frame.last) + frame.bar
    draw_direct_labels(svg, frame, [(right, y) for y in middles], [[band["label"]] for band in bands],
                       list(p.size_text), False, tops[-1], base - LABEL_SIZE / 2)

    surge_note(svg, frame, stats, tops, base)
    draw_month_axis(svg, frame, base, [f"{months[key]['prs']:,}" for key in frame.keys])
    return svg.render()


def lines_chart(stats: dict, frame: Frame, theme: Theme) -> str:
    months, keys = stats["months"], frame.keys
    base = PLOT_TOP + LINES_PLOT_HEIGHT
    first = month_start(keys[0])
    cap = f"capped at {stats['line_cap_per_pr']:,} lines per PR"
    svg = Svg(base + AXIS_GAP + 8, theme, f"Lines added and deleted per month since {first:%B %Y}, {cap}",
              SUMMARY_GAP)
    p = svg.palette
    svg.heading("Lines changed per month", cap, counted_to(stats, frame))
    values = ticks(max(months[key][kind] for key in keys for kind in ("additions", "deletions")))
    scale = LINES_PLOT_HEIGHT / values[-1]
    draw_grid(svg, frame, values, base, scale)

    surge = month_start(stats["surge_month"])
    svg.line(frame.surge_x, PLOT_TOP - 8, frame.surge_x, base, p.rule, "3 4")
    svg.text(frame.surge_x + 8, PLOT_TOP + LABEL_SIZE * 0.35 - 8, f"{surge:%b %Y}", halo=True)

    # A month still in progress gets a dashed final segment: its total is still climbing.
    partial = bool(counted_to(stats, frame))
    ends = []
    for kind, color in (("deletions", p.deleted), ("additions", p.added)):
        points = [(frame.centre(i), base - months[key][kind] * scale) for i, key in enumerate(keys)]
        solid = points[:-1] if partial else points
        svg.path("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in solid), stroke=color, width=2.5)
        if partial:
            (x1, y1), (x2, y2) = points[-2:]
            svg.path(f"M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}", stroke=color, width=2.5, dash="5 5")
        for x, y in points:
            svg.dot(x, y, color)
        ends.append((points[-1][0] + DOT, points[-1][1]))
    last = months[keys[-1]]
    names = [[compact(last["deletions"]), "deleted"], [compact(last["additions"]), "added"]]
    draw_direct_labels(svg, frame, ends, names,
                       [p.deleted, p.added], True, PLOT_TOP, base - row_height(LABEL_SIZE) / 2)

    draw_month_axis(svg, frame, base)
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
    first, latest = month_start(frame.keys[0]), month_start(frame.keys[-1])
    partial = is_partial(latest, generated)
    prs = [months[key]["prs"] for key in frame.keys]
    early = list(map(str, prs[:frame.surge]))
    before = f"{', '.join(early[:-1])} and {early[-1]}" if len(early) > 1 else early[0]
    after = [f"{months[key]['prs']} {'so far ' if partial and key == frame.keys[-1] else ''}in "
             f"{month_start(key):%B}" for key in frame.keys[frame.surge:]]
    prs_alt = (f"Merged PRs per month, stacked by lines per PR: {before} from {first:%B} to "
               f"{month_start(frame.keys[frame.surge - 1]):%B %Y}, then {', '.join(after[:-1])} and {after[-1]}")
    last = months[frame.keys[-1]]
    lines_alt = (f"Lines added and deleted per month, capped at {stats['line_cap_per_pr']:,} lines per PR: "
                 f"{compact(last['additions'])} added and {compact(last['deletions'])} deleted "
                 f"{'so far ' if partial else ''}in {latest:%B}")
    floors = {band["key"]: band["floor"] for band in stats["size_bands"]}
    return Template(TEMPLATE_FILE.read_text()).substitute(
        surge_month=surge_name,
        prs_chart=picture(Chart.PRS, prs_alt),
        lines_chart=picture(Chart.LINES, lines_alt),
        private=f"{since['private_prs']:,}",
        prs=f"{since['prs']:,}",
        repos=since["repos"],
        private_projects=f"{since['private_projects']} private project{'' if since['private_projects'] == '1' else 's'}",
        median=f"{since['median']:,}",
        p90=f"{since['p90']:,}",
        tests=round(since["test_share"] * 100),
        shipped=compact(since["lines_shipped"]),
        large=f"{since['large']:,}",
        large_floor=f"{floors['l']:,}",
        extra_large=f"{since['extra_large']:,}",
        extra_large_floor=f"{floors['xl']:,}",
        updated=f"{generated.day} {generated:%b %Y}",
        method_url=METHOD_URL,
    )


def charted_months(stats: dict) -> list[str]:
    """Every month from the baseline on, but a month in progress only once it has overtaken the one before it.

    Otherwise the first week of each month draws a near-empty bar that reads as a collapse.
    """
    keys = sorted(key for key in stats["months"] if key >= stats["baseline"]["first_month"])
    latest, previous = keys[-1], keys[-2]
    in_progress = is_partial(month_start(latest), date.fromisoformat(stats["generated"]))
    if in_progress and stats["months"][latest]["prs"] < stats["months"][previous]["prs"]:
        return keys[:-1]
    return keys


def frame_for(stats: dict, keys: list[str]) -> Frame:
    """Fit the plot between the widest gridline value of either chart and the widest direct label."""
    months, bands = stats["months"], stats["size_bands"]
    highs = [max(months[key][band["key"]] for key in keys for band in bands),
             max(months[key][kind] for key in keys for kind in ("additions", "deletions"))]
    left = PAD + max(text_width(tick_label(value), LABEL_SIZE) for high in highs for value in ticks(high)) + 10
    last = months[keys[-1]]
    labels = [*(band["label"] for band in bands), "deleted", "added"]
    widest = max(*(text_width(label, LABEL_SIZE) for label in labels),
                 *(text_width(compact(last[kind]), LABEL_SIZE, True) for kind in ("additions", "deletions")))
    return Frame(keys, keys.index(stats["surge_month"]), left, LEADER + widest)


def main() -> None:
    stats = json.loads(STATS_FILE.read_text())
    keys = charted_months(stats)
    frame = frame_for(stats, keys)
    ASSETS_DIR.mkdir(exist_ok=True)
    for theme in Theme:
        (ASSETS_DIR / f"{Chart.PRS}-{theme}.svg").write_text(pr_chart(stats, frame, theme))
        (ASSETS_DIR / f"{Chart.LINES}-{theme}.svg").write_text(lines_chart(stats, frame, theme))
    README_FILE.write_text(readme(stats, frame))


if __name__ == "__main__":
    main()
