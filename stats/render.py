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

CHART_WIDTH = 560
DISPLAY_WIDTH = CHART_WIDTH
PAD = 4
LABEL_SIZE = 19
TOTAL_SIZE = 20
TITLE_SIZE = 22
LINE_HEIGHT = 1.3
TEXT_GAP = 4
WINDOW_MONTHS = 12
TITLE_Y = 22
UNIT_Y = 48
PLOT_TOP = 92
NOTE_TOP = PLOT_TOP + 6
PR_PLOT_HEIGHT = 262
LINES_PLOT_HEIGHT = 190
AXIS_GAP = 28
YEAR_GAP = 22
TOTALS_GAP = 26
BAR_SHARE = 0.56
SEGMENT_GAP = 2
MIN_SEGMENT = 3
RADIUS = 2
LEADER = 12
DOT = 4.5
SPACE_UNDER_SUMMARY = 12
FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif'


class Theme(StrEnum):
    LIGHT = "light"
    DARK = "dark"


class Chart(StrEnum):
    PRS = "prs"
    LINES = "lines"


class LineKind(StrEnum):
    ADDITIONS = "additions"
    DELETIONS = "deletions"


LINE_NAMES = {LineKind.ADDITIONS: "added", LineKind.DELETIONS: "deleted"}


class SizeKey(StrEnum):
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"


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
    size_ramp: tuple[str, str, str, str]
    legible_sizes: tuple[str, str, str, str]
    added: str
    deleted: str


PALETTES = {
    Theme.LIGHT: Palette("#1f1c19", "#665f58", "#ffffff", "#e8e4df", "#b8afa6",
                         ("#cf7d5a", "#b45733", "#8b3f23", "#612a17"),
                         ("#b65b35", "#b45733", "#8b3f23", "#612a17"), "#24773f", "#b5532f"),
    Theme.DARK: Palette("#efebe7", "#a39c95", "#0d1117", "#2a2928", "#57524d",
                        ("#935038", "#c46945", "#de9474", "#f5c6ae"),
                        ("#ba6748", "#c46945", "#de9474", "#f5c6ae"), "#5fc68a", "#e08463"),
}


def noto_sans_width(text: str, size: float, bold: bool = False) -> float:
    em = sum(0.27 if ch == " " else 0.32 if ch in "ilI.,:;|'()[]" else 0.85 if ch in "mwMW–"
             else 0.62 if ch.isupper() or ch.isdigit() else 0.55 for ch in text)
    return em * size * (1.02 if bold else 1)




def band_label(band: dict) -> str:
    return f"{band['label']} lines"


def compact(n: int) -> str:
    if n >= 999_500:
        return f"{n / 1e6:.1f}M"
    return f"{round(n / 1000)}k" if n >= 1000 else str(n)


def short_total(n: int, decimals: bool) -> str:
    if n < 1000 or n >= 9_950 or not decimals:
        return compact(n) if n >= 1000 else str(n)
    return f"{n / 1000:.1f}".removesuffix(".0") + "k"


def exact_tick(n: int) -> str:
    return f"{n / 1e6:g}M" if n >= 1_000_000 else f"{n / 1000:g}k" if n >= 1000 else str(n)


def ticks(highest: int) -> list[int]:
    raw = max(highest, 1) / 4
    magnitude = 10 ** math.floor(math.log10(raw))
    step = max(1, next(m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw))
    return [round(step * i) for i in range(math.ceil(max(highest, 1) / step) + 1)]


def month_start(key: str) -> date:
    return date.fromisoformat(f"{key}-01")


def wrappable_pieces(phrases: list[str], size: float, width: float, bold: bool) -> list[str]:
    return [word for phrase in phrases
            for word in ([phrase] if noto_sans_width(phrase, size, bold) <= width else phrase.split())]


def greedy_wrap(pieces: list[str], size: float, width: float, bold: bool) -> list[str]:
    rows: list[str] = []
    for piece in pieces:
        if rows and noto_sans_width(f"{rows[-1]} {piece}", size, bold) <= width:
            rows[-1] += f" {piece}"
        else:
            rows.append(piece)
    return rows


def balanced_rows(phrases: list[str], size: float, width: float, bold: bool) -> list[str]:
    pieces = wrappable_pieces(phrases, size, width, bold)
    rows = greedy_wrap(pieces, size, width, bold)
    while True:
        narrower = greedy_wrap(pieces, size, max(noto_sans_width(row, size, bold) for row in rows) - 1, bold)
        if len(narrower) != len(rows) or narrower == rows:
            return rows
        rows = narrower


def spread(wanted: list[float], gap: float, low: float, high: float) -> list[float]:
    def clash(top: list[float], bottom: list[float]) -> bool:
        return sum(top) / len(top) + len(top) * gap / 2 > sum(bottom) / len(bottom) - len(bottom) * gap / 2

    touching_runs: list[list[float]] = []
    for y in wanted:
        touching_runs.append([y])
        while len(touching_runs) > 1 and clash(touching_runs[-2], touching_runs[-1]):
            touching_runs[-2:] = [touching_runs[-2] + touching_runs[-1]]
    ys = [sum(g) / len(g) + (i - (len(g) - 1) / 2) * gap for g in touching_runs for i in range(len(g))]
    for i, y in enumerate(ys):
        ys[i] = max(y, low if i == 0 else ys[i - 1] + gap)
    for i in reversed(range(len(ys))):
        ys[i] = min(ys[i], high if i == len(ys) - 1 else ys[i + 1] - gap)
    return ys


def bar_path(x: float, y: float, width: float, height: float, round_top: bool) -> str:
    r = min(RADIUS, width / 2, height) if round_top else 0
    return (f"M{x:.1f},{y + height:.1f}V{y + r:.1f}Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f}H{x + width - r:.1f}"
            f"Q{x + width:.1f},{y:.1f} {x + width:.1f},{y + r:.1f}V{y + height:.1f}Z")


def row_height(size: float) -> float:
    return size * LINE_HEIGHT


class Svg:
    def __init__(self, theme: Theme, label: str, space_above: int = 0):
        self.palette, self.label, self.parts = PALETTES[theme], label, []
        self.space_above = space_above

    def text(self, x, y, text, size=LABEL_SIZE, fill="", anchor=Anchor.START, bold=False, halo=False):
        width = noto_sans_width(text, size, bold)
        left = {Anchor.START: x, Anchor.MIDDLE: x - width / 2, Anchor.END: x - width}[anchor]
        x += max(PAD - left, 0) + min(CHART_WIDTH - PAD - (left + width), 0)
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
        p = self.palette
        self.text(PAD, TITLE_Y, title, TITLE_SIZE, p.ink, bold=True)
        self.text(PAD, UNIT_Y, unit)
        if note:
            self.text(CHART_WIDTH - PAD, TITLE_Y, note, anchor=Anchor.END)

    def render(self, bottom: float) -> str:
        style = f"text{{font-family:{FONT};font-variant-numeric:tabular-nums}}"
        height = math.ceil(bottom) + self.space_above
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CHART_WIDTH} {height}" '
                f'width="{CHART_WIDTH}" height="{height}" role="img" aria-label="{escape(self.label)}">'
                f'<style>{style}</style><g transform="translate(0 {self.space_above})">{"".join(self.parts)}</g>'
                '</svg>\n')


@dataclass(frozen=True)
class Frame:
    keys: list[str]
    surge: int | None
    left: float
    gutter: float

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


def draw_grid(svg: Svg, frame: Frame, values: list[int], base: float, scale: float) -> None:
    for value in values:
        y = base - value * scale
        if value:
            svg.line(frame.left, y, CHART_WIDTH - PAD, y, svg.palette.grid, "2 6")
        svg.text(frame.left - 10, y + LABEL_SIZE * 0.35, exact_tick(value), anchor=Anchor.END)
    svg.line(frame.left, base, CHART_WIDTH - PAD, base, svg.palette.rule)


@dataclass(frozen=True)
class EndLabel:
    x: float
    y: float
    rows: list[str]
    color: str


def draw_direct_labels(svg: Svg, frame: Frame, labels: list[EndLabel], bold_first: bool, low: float,
                       high: float) -> None:
    rh = row_height(LABEL_SIZE)
    ordered = sorted(labels, key=lambda label: label.y)
    ys = spread([label.y for label in ordered], max(rh * len(label.rows) for label in labels), low, high)
    column = frame.right + LEADER
    for label, y in zip(ordered, ys):
        svg.path(f"M{label.x:.1f},{label.y:.1f}H{label.x + 4:.1f}L{column - 5:.1f},{y:.1f}", stroke=svg.palette.rule)
        first = y + LABEL_SIZE * 0.35 - (len(label.rows) - 1) * rh / 2
        for k, row in enumerate(label.rows):
            svg.text(column, first + k * rh, row, fill=label.color, bold=bold_first and k == 0)


def fits(texts: list[str], size: float, bold: bool, step: float) -> bool:
    widths = [noto_sans_width(text, size, bold) for text in texts]
    return all((a + b) / 2 + TEXT_GAP <= step for a, b in zip(widths, widths[1:]))


def opens_year(key: str, keys: list[str]) -> bool:
    return key == keys[0] or month_start(key).month == 1


def year_marks(frame: Frame) -> dict[int, str]:
    marks = {i: f"{month_start(key):%Y}" for i, key in enumerate(frame.keys) if opens_year(key, frame.keys)}
    if 1 in marks and 0 in marks and not fits([marks[0], marks[1]], LABEL_SIZE, False, frame.step):
        del marks[0]
    return marks


def draw_month_axis(svg: Svg, frame: Frame, base: float, counts: list[int] | None = None) -> float:
    names = [f"{month_start(key):%b}" for key in frame.keys]
    if not fits(names, LABEL_SIZE, False, frame.step):
        names = [name[0] for name in names]
    for i, name in enumerate(names):
        svg.text(frame.centre(i), base + AXIS_GAP, name, anchor=Anchor.MIDDLE)
    for i, year in year_marks(frame).items():
        svg.text(frame.centre(i), base + AXIS_GAP + YEAR_GAP, year, anchor=Anchor.MIDDLE)
    bottom = base + AXIS_GAP + YEAR_GAP
    if not counts:
        return bottom
    layouts = [([short_total(n, decimals) for n in counts], row_count) for decimals in (True, False)
               for row_count in (1, 2)]
    totals, row_count = next(((totals, row_count) for totals, row_count in layouts
                              if all(fits(totals[i::row_count], TOTAL_SIZE, True, frame.step * row_count)
                                     for i in range(row_count))), layouts[-1])
    for i, total in enumerate(totals):
        svg.text(frame.centre(i), bottom + TOTALS_GAP * (1 + i % row_count), total, TOTAL_SIZE, svg.palette.ink,
                 Anchor.MIDDLE, True)
    return bottom + TOTALS_GAP * row_count


def counted_to(stats: dict, frame: Frame) -> str:
    generated, latest = date.fromisoformat(stats["generated"]), month_start(frame.keys[-1])
    return f"counted to {latest:%b} {generated.day}" if is_partial(latest, generated) else ""


@dataclass(frozen=True)
class Note:
    rows: list[str]
    x: float
    anchor: Anchor

    @property
    def width(self) -> float:
        return max(noto_sans_width(row, LABEL_SIZE, True) for row in self.rows)

    @property
    def left(self) -> float:
        return self.x if self.anchor == Anchor.START else self.x - self.width

    @property
    def bottom(self) -> float:
        return NOTE_TOP + (len(self.rows) - 1) * row_height(LABEL_SIZE) + LABEL_SIZE * 0.3


def note_options(frame: Frame, stats: dict) -> list[Note]:
    surge = month_start(stats["surge_month"])
    words = [f"{surge:%b %Y}:", *"started building my agent workflow".split()]
    spots = [(frame.surge_x + 12, Anchor.START), (frame.surge_x - 12, Anchor.END), (frame.left, Anchor.START)]
    options = []
    for count in (2, 3, 4):
        for x, anchor in spots:
            notes = (Note(balanced_rows(words, LABEL_SIZE, width, True), x, anchor) for width in range(120, 340, 4))
            note = next((note for note in notes if len(note.rows) == count and frame.left - 1 <= note.left
                         and note.left + note.width <= CHART_WIDTH - PAD), None)
            if note:
                options.append(note)
    return options


def clears_bars(note: Note, frame: Frame, tops: list[float]) -> bool:
    return all(top > note.bottom + 10 for i, top in enumerate(tops)
               if frame.bar_left(i) < note.left + note.width and frame.bar_left(i) + frame.bar > note.left)


def place_surge_note(frame: Frame, stats: dict, tops: list[float]) -> tuple[Note, float]:
    options = note_options(frame, stats)
    clear = next((note for note in options if clears_bars(note, frame, tops)), None)
    return (clear, 0) if clear else (options[0], options[0].bottom + 14 - PLOT_TOP)


def draw_surge_note(svg: Svg, frame: Frame, note: Note, base: float) -> None:
    crosses = note.left < frame.surge_x < note.left + note.width
    top = note.bottom + 10 if crosses else NOTE_TOP - LABEL_SIZE * 0.8
    svg.line(frame.surge_x, top, frame.surge_x, base, svg.palette.rule, "3 4")
    svg.rows(note.x, NOTE_TOP, note.rows, LABEL_SIZE, svg.palette.ink, note.anchor, True)


@dataclass(frozen=True)
class Segment:
    top: float
    height: float
    middle: float


def stacked(month: dict, bands: list[dict], scale: float, base: float) -> list[Segment]:
    segments, floor = [], base
    for band in bands:
        count = month[band["key"]]
        height = max(count * scale, MIN_SEGMENT) if count else 0
        gap_below = SEGMENT_GAP if height and floor < base else 0
        segments.append(Segment(floor - height, height - gap_below, floor - (height + gap_below) / 2))
        floor -= height
    return segments


def pr_chart(stats: dict, frame: Frame, theme: Theme) -> str:
    months, bands = stats["months"], stats["size_bands"]
    first = month_start(frame.keys[0])
    svg = Svg(theme, f"Merged pull requests per month since {first:%B %Y}, stacked by lines per PR")
    p = svg.palette
    svg.heading("Merged PRs per month", "stacked by lines changed per PR", counted_to(stats, frame))
    values = pr_ticks(stats, frame.keys)
    scale = PR_PLOT_HEIGHT / values[-1]

    def stacks_on(base: float) -> list[list[Segment]]:
        return [stacked(months[key], bands, scale, base) for key in frame.keys]

    base = PLOT_TOP + PR_PLOT_HEIGHT
    note, room = (place_surge_note(frame, stats, [stack[-1].top for stack in stacks_on(base)]) if frame.surge
                  else (None, 0))
    base += room
    stacks = stacks_on(base)
    draw_grid(svg, frame, values, base, scale)
    for i, stack in enumerate(stacks):
        highest = max((j for j, segment in enumerate(stack) if segment.height), default=-1)
        for j, segment in enumerate(stack):
            if segment.height:
                svg.path(bar_path(frame.bar_left(i), segment.top, frame.bar, segment.height, j == highest),
                         p.size_ramp[j])
    tops = [stack[-1].top for stack in stacks]
    right = frame.bar_left(frame.last) + frame.bar
    latest_band_labels = [EndLabel(right, segment.middle, [band_label(band)], color)
                          for segment, band, color in zip(stacks[-1], bands, p.legible_sizes)]
    draw_direct_labels(svg, frame, latest_band_labels, False, tops[-1], base - LABEL_SIZE / 2)

    if note:
        draw_surge_note(svg, frame, note, base)
    bottom = draw_month_axis(svg, frame, base, [months[key]["prs"] for key in frame.keys])
    return svg.render(bottom + 8)


def lines_chart(stats: dict, frame: Frame, theme: Theme) -> str:
    months, keys = stats["months"], frame.keys
    base = PLOT_TOP + LINES_PLOT_HEIGHT
    first = month_start(keys[0])
    cap = f"capped at {stats['line_cap_per_pr']:,} lines per PR"
    svg = Svg(theme, f"Lines added and deleted per month since {first:%B %Y}, {cap}", SPACE_UNDER_SUMMARY)
    p = svg.palette
    svg.heading("Lines changed per month", cap, counted_to(stats, frame))
    values = line_ticks(stats, keys)
    scale = LINES_PLOT_HEIGHT / values[-1]
    draw_grid(svg, frame, values, base, scale)

    if frame.surge:
        surge = month_start(stats["surge_month"])
        svg.line(frame.surge_x, PLOT_TOP - 8, frame.surge_x, base, p.rule, "3 4")
        svg.text(frame.surge_x + 8, PLOT_TOP + LABEL_SIZE * 0.35 - 8, f"{surge:%b %Y}", halo=True)

    still_climbing = bool(counted_to(stats, frame))
    ends = []
    for kind, color in ((LineKind.DELETIONS, p.deleted), (LineKind.ADDITIONS, p.added)):
        points = [(frame.centre(i), base - months[key][kind] * scale) for i, key in enumerate(keys)]
        solid = points[:-1] if still_climbing else points
        svg.path("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in solid), stroke=color, width=2.5)
        if still_climbing:
            (x1, y1), (x2, y2) = points[-2:]
            svg.path(f"M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}", stroke=color, width=2.5, dash="5 5")
        for x, y in points:
            svg.dot(x, y, color)
        x, y = points[-1]
        ends.append(EndLabel(x + DOT, y, [compact(months[keys[-1]][kind]), LINE_NAMES[kind]], color))
    draw_direct_labels(svg, frame, ends, True, PLOT_TOP, base - row_height(LABEL_SIZE) / 2)

    return svg.render(draw_month_axis(svg, frame, base) + 8)


def picture(chart: Chart, alt: str) -> str:
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{chart}-{Theme.DARK}.svg">'
            f'<img src="assets/{chart}-{Theme.LIGHT}.svg" alt="{escape(alt)}" width="{DISPLAY_WIDTH}"></picture>')


def is_partial(month: date, generated: date) -> bool:
    return (month.year, month.month) == (generated.year, generated.month)


def listed(items: list[str]) -> str:
    return f"{', '.join(items[:-1])} and {items[-1]}" if len(items) > 1 else items[0]


def spans_years(keys: list[str]) -> bool:
    return month_start(keys[0]).year != month_start(keys[-1]).year


def spoken(key: str, keys: list[str], with_year: bool = False) -> str:
    start = month_start(key)
    named = with_year or spans_years(keys) and opens_year(key, keys)
    return f"{start:%B %Y}" if named else f"{start:%B}"


def prs_alt(months: dict, frame: Frame, partial: bool) -> str:
    keys = frame.keys
    early, late = keys[:frame.surge or 0], keys[frame.surge or 0:]
    year_once = None if spans_years(keys) else (early or late)[-1]

    def name(key: str) -> str:
        return spoken(key, keys, key == year_once)

    counts = listed([f"{months[key]['prs']:,} {'so far ' if partial and key == keys[-1] else ''}in {name(key)}"
                     for key in late])
    if not early:
        return f"Merged PRs per month, stacked by lines per PR: {counts}"
    early_counts = listed([format(months[key]["prs"], ",") for key in early])
    before = (f"{early_counts} in {name(early[0])}" if len(early) == 1 else
              f"{early_counts} from {name(early[0])} to {name(early[-1])}")
    return f"Merged PRs per month, stacked by lines per PR: {before}, then {counts}"


def readme(stats: dict, frame: Frame) -> str:
    months, since = stats["months"], stats["since_surge"]
    generated = date.fromisoformat(stats["generated"])
    surge = month_start(stats["surge_month"])
    surge_name = f"{surge:%B}" if surge.year == generated.year else f"{surge:%B %Y}"
    latest = month_start(frame.keys[-1])
    partial = is_partial(latest, generated)
    last = months[frame.keys[-1]]
    lines_alt = (f"Lines added and deleted per month, capped at {stats['line_cap_per_pr']:,} lines per PR: "
                 f"{compact(last[LineKind.ADDITIONS])} added and {compact(last[LineKind.DELETIONS])} deleted "
                 f"{'so far ' if partial else ''}in {spoken(frame.keys[-1], frame.keys, spans_years(frame.keys))}")
    floors = {band["key"]: band["floor"] for band in stats["size_bands"]}
    return Template(TEMPLATE_FILE.read_text()).substitute(
        surge_month=surge_name,
        prs_chart=picture(Chart.PRS, prs_alt(months, frame, partial)),
        lines_chart=picture(Chart.LINES, lines_alt),
        private=f"{since['private_prs']:,}",
        prs=f"{since['prs']:,}",
        repos=since["repos"],
        private_projects=f"{since['private_projects']} private "
                         f"project{'' if since['private_projects'] == '1' else 's'}",
        median=f"{since['median']:,}",
        p90=f"{since['p90']:,}",
        tests=math.floor(since["test_share"] * 100 + 0.5),
        shipped=compact(since["lines_shipped"]),
        large=f"{since['large']:,}",
        large_floor=f"{floors[SizeKey.L]:,}",
        extra_large=f"{since['extra_large']:,}",
        extra_large_floor=f"{floors[SizeKey.XL]:,}",
        updated=f"{generated.day} {generated:%b %Y}",
        method_url=METHOD_URL,
    )


def charted_months(stats: dict) -> list[str]:
    keys = sorted(key for key in stats["months"] if key >= stats["baseline"]["first_month"])
    latest, previous = keys[-1], keys[-2]
    in_progress = is_partial(month_start(latest), date.fromisoformat(stats["generated"]))
    still_catching_up = in_progress and stats["months"][latest]["prs"] <= stats["months"][previous]["prs"]
    return (keys[:-1] if still_catching_up else keys)[-WINDOW_MONTHS:]


def pr_ticks(stats: dict, keys: list[str]) -> list[int]:
    return ticks(max(stats["months"][key]["prs"] for key in keys))


def line_ticks(stats: dict, keys: list[str]) -> list[int]:
    return ticks(max(stats["months"][key][kind] for key in keys for kind in LineKind))


def frame_for(stats: dict, keys: list[str]) -> Frame:
    months, bands = stats["months"], stats["size_bands"]
    drawn = [*pr_ticks(stats, keys), *line_ticks(stats, keys)]
    left = PAD + max(noto_sans_width(exact_tick(value), LABEL_SIZE) for value in drawn) + 10
    last = months[keys[-1]]
    labels = [*(band_label(band) for band in bands), *LINE_NAMES.values()]
    widest = max(*(noto_sans_width(label, LABEL_SIZE) for label in labels),
                 *(noto_sans_width(compact(last[kind]), LABEL_SIZE, True) for kind in LineKind))
    surge = keys.index(stats["surge_month"]) if stats["surge_month"] in keys[1:] else None
    return Frame(keys, surge, left, LEADER + widest)


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
