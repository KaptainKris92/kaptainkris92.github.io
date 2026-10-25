"""Builds the Night Shift post's charts as inline HTML/SVG includes.

Usage: python make_charts.py <approvals.json> <out_dir>
Re-run after the stats change to refresh the numbers.
"""
import json, sys, html
from pathlib import Path

approvals, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
runs = json.loads(approvals.read_text())["runs"]

rows = []
for run_id, r in runs.items():
    s = r.get("stats") or {}
    ig, yt = s.get("instagram") or {}, s.get("youtube") or {}
    if "views" not in ig:
        continue
    name = " ".join(w.capitalize() for w in run_id.split("-")[2:])
    day = f"{int(run_id[6:8])} Oct"
    rows.append(dict(name=name, day=day, ig=ig["views"], yt=yt.get("views") or 0,
                     igw=ig.get("ig_reels_avg_watch_time", 0) / 1000,
                     skip=ig.get("reels_skip_rate"), at=ig.get("at", "")[:10]))
asof = max(r["at"] for r in rows)
asof_txt = f"{int(asof[8:10])} October {asof[:4]}"

def esc(x): return html.escape(str(x), quote=True)
def fmt(n): return f"{n:,}"

def panel(rows, key, cls, label, cap, step, tick_fmt, tip_fmt, title_id, marker=None, direct=None):
    """One horizontal-bar panel: a row per video, oldest at the top."""
    LW, PW, RH, TOP, F = 150, 226, 30, 26, 13.5
    gap = 22 if marker else 0
    W, H = LW + PW + 14, TOP + RH * len(rows) + 28 + gap
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="{title_id}">',
         f'<text class="label-strong" x="{LW}" y="15" font-size="{F}">{label}</text>']
    for t in range(0, cap + 1, step):
        x = LW + PW * t / cap
        o.append(f'<line class="gridline" x1="{x:.1f}" x2="{x:.1f}" y1="{TOP}" y2="{H-24}"/>')
        o.append(f'<text class="tick" x="{x:.1f}" y="{H-6}" font-size="12.5" text-anchor="middle">{tick_fmt(t)}</text>')
    o.append(f'<line class="baseline" x1="{LW}" x2="{LW}" y1="{TOP}" y2="{H-24}"/>')
    shift = 0
    for i, r in enumerate(rows):
        if marker and r["name"] == marker[0]:
            shift = gap
            ly = TOP + i * RH + 4 + gap
            o.append(f'<line x1="0" x2="{W}" y1="{ly}" y2="{ly}" stroke="var(--muted)" stroke-width="1"/>')
            o.append(f'<text x="0" y="{ly-6}" font-size="12.5">{marker[1]}</text>')
        v, y = r[key], TOP + i * RH + 7 + shift
        w = max(PW * min(v, cap) / cap, 1.5)
        o.append(f'<rect class="hit" x="0" y="{y-5}" width="{W}" height="{RH}" data-tip="{esc(tip_fmt(r))}"/>')
        o.append(f'<rect class="mark {cls}" x="{LW}" y="{y}" width="{w:.1f}" height="{RH-12}" rx="3" pointer-events="none"/>')
        o.append(f'<text x="0" y="{y+13}" font-size="{F}" pointer-events="none">{esc(r["name"])}</text>')
        if v > cap:
            bx = LW + PW - 18
            o.append(f'<path d="M{bx} {y+RH-10} l6 -{RH-8} M{bx+6} {y+RH-10} l6 -{RH-8}" stroke="var(--surface)" stroke-width="3" pointer-events="none"/>')
            o.append(f'<text x="{LW+PW-26}" y="{y+13}" font-size="13" font-weight="650" text-anchor="end" style="fill:#fff" pointer-events="none">{fmt(v)}</text>')
        elif direct and r is direct:
            o.append(f'<text class="label-strong" x="{LW+w+6:.1f}" y="{y+13}" font-size="13" pointer-events="none">{v:.1f}s</text>')
    o.append("</svg>")
    return "".join(o)

def figure(title_id, title, sub, legend, panels, headers, table_rows, style=""):
    leg = "".join(f'<li><span class="chart__key" style="background:var(--series-{n})"></span>{t}</li>' for n, t in legend)
    leg = f'<ul class="chart__legend">{leg}</ul>' if legend else ""
    th = "".join(f"<th>{h}</th>" for h in headers)
    return f'''<figure class="chart wide figure" data-chart{style}>
  <p class="chart__title" id="{title_id}">{title}</p>
  <p class="chart__sub">{sub}</p>
  {leg}
  <div class="chart__panels">{"".join(panels)}</div>
  <details><summary>Show the numbers</summary><table><thead><tr>{th}</tr></thead><tbody>{table_rows}</tbody></table></details>
</figure>
'''

kfmt = lambda t: "0" if t == 0 else f"{t//1000}k"
views = figure("views-title", "Views per video",
    f"Every posted sighting so far, from 13 October (top) to 24 October. Both panels share one scale, so Sett Grub's Instagram bar is cut off at 4k. Stats as of {asof_txt}.",
    [(1, "Instagram Reels"), (2, "YouTube Shorts")],
    [panel(rows, "ig", "s1", "Instagram", 4000, 1000, kfmt, lambda r: f"{r['name']} ({r['day']})\nInstagram: {fmt(r['ig'])} views", "views-title"),
     panel(rows, "yt", "s2", "YouTube", 4000, 1000, kfmt, lambda r: f"{r['name']} ({r['day']})\nYouTube: {fmt(r['yt'])} views", "views-title")],
    ["Video", "Posted", "Instagram", "YouTube"],
    "".join(f"<tr><td>{esc(r['name'])}</td><td>{r['day']}</td><td>{fmt(r['ig'])}</td><td>{fmt(r['yt'])}</td></tr>" for r in rows),
    ' style="max-width:52rem"')
(out / "nightshift-views.html").write_text(views)

best = max(rows, key=lambda r: r["igw"])
watch = figure("watch-title", "Average Instagram watch time",
    "Seconds watched per view, out of a 15-second video, oldest at the top. Hover or tap a row for the share of viewers who skipped in the first 3 seconds.",
    [],
    [panel(rows, "igw", "s1", "Seconds watched", 15, 5, lambda t: f"{t}s",
           lambda r: f"{r['name']} ({r['day']})\nAverage watch: {r['igw']:.1f} s\nSkipped in first 3 s: {r['skip']}%",
           "watch-title", marker=("Skep Listener", "Opens on the creature from here"), direct=best)],
    ["Video", "Posted", "Average watch", "Skipped in 3 s"],
    "".join(f"<tr><td>{esc(r['name'])}</td><td>{r['day']}</td><td>{r['igw']:.1f} s</td><td>{r['skip']}%</td></tr>" for r in rows),
    ' style="max-width:34rem"')
(out / "nightshift-watch.html").write_text(watch)
print(len(rows), "videos, stats as of", asof)
