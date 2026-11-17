"""Generate docs/how-it-works-{light,dark}.svg — the README's "how it works" picture.

One template, two palettes (GitHub light and dark), so the pair can't drift.
Sized to GitHub's README column (~830 px), so it shows close to 1:1 and the
text stays readable. Edit PHASES / DAILY below, then run from the repo root:

    python3 scripts/build_readme_infographic.py docs
"""
import sys
from html import escape
from pathlib import Path

W = 820
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

# (name, when, commands, what you get — one string per line)
PHASES = [
    ("Set up", "once · 10–15 min", ["/setup"],
     ["profile, strategy, scoring rubric", "pre-filled from your CV"]),
    ("Find & score", "weekly", ["/job-search", "/evaluate-position"],
     ["a folder per company", "tier P0–P2 + research brief"]),
    ("Apply", "per role", ["/apply", "/ats-check", "/cover-letter", "/sent"],
     ["tailored CV + PDF, ATS-checked", "frozen copy of what you sent"]),
    ("Interview", "per round", ["/interview-prep", "/case-practice", "simulator", "/interview-analysis"],
     ["stories adapted to the round", "mock rounds, quoted debrief"]),
    ("Decide", "at the offer", ["/evaluate-offer", "/wrap-up"],
     ["verdict + negotiation moves", "withdrawals, thank-yous, retro"]),
]

DAILY = [
    ("/today", "morning brief, follow-ups due"),
    ("/follow-up", "nudge a quiet application"),
    ("/outreach", "referral asks, thank-yous"),
    ("/dashboard", "the pipeline at a glance"),
    ("career-coach", "when the search is stuck"),
]

PALETTES = {
    "light": dict(card="#f6f8fa", border="#d0d7de", text="#1f2328", muted="#59636e",
                  accent="#0969da", accent_bg="#ddf4ff", badge="#0969da", badge_text="#ffffff",
                  line="#d0d7de", ok="#1a7f37"),
    "dark": dict(card="#161b22", border="#30363d", text="#e6edf3", muted="#9198a1",
                 accent="#79c0ff", accent_bg="#0c2d6b", badge="#4493f8", badge_text="#0d1117",
                 line="#30363d", ok="#3fb950"),
}

# layout
PAD = 16
X_BADGE = 34
X_NAME = 64
X_CMDS = 236
CMDS_MAX = 560        # commands wrap before this x
X_GET = 580
MONO_W = 7.85         # px per char at 13 px monospace
PILL_H, PILL_GAP, LINE_GAP = 22, 6, 8
GET_LH = 20


def t(x, y, s, *, size=13, fill, weight=400, family=FONT, anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')


def pill(x, y, label, p):
    w = 10 + MONO_W * len(label)
    return [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{PILL_H}" rx="6" fill="{p["accent_bg"]}"/>',
            t(x + 5, y + 15.5, label, family=MONO, fill=p["accent"])], w


def layout_cmds(cmds):
    """Wrap command pills into lines; returns [(x_offset, line_index, label)]."""
    out, x, line = [], X_CMDS, 0
    for c in cmds:
        w = 10 + MONO_W * len(c)
        if x > X_CMDS and x + w > CMDS_MAX:
            x, line = X_CMDS, line + 1
        out.append((x, line, c))
        x += w + PILL_GAP
    return out


def svg(p):
    body, y = [], PAD
    # column headers
    for x, label in ((X_NAME, "PHASE"), (X_CMDS, "YOU RUN"), (X_GET, "YOU GET")):
        body.append(t(x, y + 12, label, size=11, weight=700, fill=p["muted"]))
    y += 26

    rows = []
    for name, when, cmds, gets in PHASES:
        placed = layout_cmds(cmds)
        n_lines = placed[-1][1] + 1
        h = max(n_lines * (PILL_H + LINE_GAP) - LINE_GAP, len(gets) * GET_LH, 40) + 28
        rows.append((y, h, name, when, placed, gets))
        y += h + 10

    # timeline spine behind the badges
    first_c = rows[0][0] + 28
    last_c = rows[-1][0] + 28
    body.append(f'<line x1="{X_BADGE}" y1="{first_c}" x2="{X_BADGE}" y2="{last_c}" '
                f'stroke="{p["line"]}" stroke-width="2"/>')

    for i, (ry, h, name, when, placed, gets) in enumerate(rows):
        body.append(f'<rect x="{X_NAME - 12}" y="{ry}" width="{W - X_NAME - 4}" height="{h}" rx="10" '
                    f'fill="{p["card"]}" stroke="{p["border"]}"/>')
        cy = ry + 28
        body.append(f'<circle cx="{X_BADGE}" cy="{cy}" r="14" fill="{p["badge"]}"/>')
        body.append(t(X_BADGE, cy + 5, str(i + 1), size=14, weight=700, fill=p["badge_text"], anchor="middle"))
        body.append(t(X_NAME, ry + 27, name, size=16, weight=700, fill=p["text"]))
        body.append(t(X_NAME, ry + 46, when, size=12, fill=p["muted"]))
        for x, line, label in placed:
            parts, _ = pill(x, ry + 14 + line * (PILL_H + LINE_GAP), label, p)
            body += parts
        for k, g in enumerate(gets):
            gy = ry + 29 + k * GET_LH
            body.append(f'<circle cx="{X_GET + 3}" cy="{gy - 4.5}" r="3" fill="{p["ok"]}"/>')
            body.append(t(X_GET + 13, gy, g, fill=p["text"]))

    # alongside band
    y += 6
    body.append(t(X_NAME, y + 12, "ALONGSIDE, EVERY DAY", size=11, weight=700, fill=p["muted"]))
    y += 24
    col = (W - X_NAME) / 2
    for k, (cmd, what) in enumerate(DAILY):
        cx = X_NAME + (k % 2) * col
        cy = y + (k // 2) * (PILL_H + 10)
        parts, w = pill(cx, cy, cmd, p)
        body += parts
        body.append(t(cx + w + 10, cy + 15.5, what, fill=p["text"]))
    y += ((len(DAILY) + 1) // 2) * (PILL_H + 10) + 14
    body.append(t(X_NAME, y + 6, "Everything is markdown in userdata/ on your machine. "
                  "Nothing is sent or changed without your yes.", size=12, fill=p["muted"]))
    H = int(y + PAD + 6)

    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-labelledby="t d">',
            '<title id="t">How job-offer works</title>',
            '<desc id="d">Five phases in order — set up, find and score, apply, interview, decide — '
            'with the commands for each and what you get, plus the tools that run alongside every day.</desc>']
    return "\n".join(head + body + ["</svg>"]) + "\n"


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    for name, pal in PALETTES.items():
        path = out / f"how-it-works-{name}.svg"
        path.write_text(svg(pal), encoding="utf-8")
        print(path)
