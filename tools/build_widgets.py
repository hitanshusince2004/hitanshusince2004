#!/usr/bin/env python3
"""
Regenerates the two hand-made widgets used in README.md:

    assets/terminal.svg   animated "terminal" intro card
    assets/skills.svg     animated skill-level bars

Edit TERMINAL_LINES / SKILLS below, then run from the repo root:

    python tools/build_widgets.py

No third-party packages needed. Both SVGs are self-contained, so they never
depend on an external service and cannot break.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

# ───────────────────────── palette ─────────────────────────
BG_DEEP, BG_MID, BORDER = "#0a0f1f", "#14213d", "#1b2a4e"
AMBER, SKY = "#fca311", "#4cc9f0"
TEXT, MUTED = "#e6edf7", "#a8b2c7"

# ───────────────────── 1. TERMINAL CARD ────────────────────
# ("cmd", text) is typed slowly after a "$ " prompt.
# ("out", text) is the command output and types faster.
TERMINAL_LINES = [
    ("cmd", "whoami"),
    ("out", "Hitanshu Kanabar — Full Stack Developer"),
    ("cmd", "cat education.txt"),
    ("out", "B.Tech IT @ K. J. Somaiya Institute of Technology"),
    ("cmd", "ls ./focus"),
    ("out", "full-stack/  devops/  cloud/"),
    ("cmd", "echo $STATUS"),
    ("out", "open to internships & opportunities"),
]

# ───────────────────── 2. SKILL BARS ───────────────────────
# (label, percent 0-100, word shown on the right)
# These are starting guesses based on your repos. Be honest, edit freely.
SKILLS = [
    ("HTML & CSS",              90, "Advanced"),
    ("JavaScript",              80, "Strong"),
    ("React",                   70, "Solid"),
    ("Node.js & Express",       70, "Solid"),
    ("MongoDB & MySQL",         65, "Solid"),
    ("Python & Java",           60, "Comfortable"),
    ("Docker, Jenkins, CI/CD",  50, "Learning"),
    ("AWS & GCP",               35, "Exploring"),
]

MONO = "'SF Mono','Cascadia Mono','DejaVu Sans Mono',Consolas,'Courier New',monospace"
SANS = "'Segoe UI',Helvetica,Arial,sans-serif"


def build_terminal() -> str:
    fs, cw, lh = 16, 9.6, 30          # font size, char width (0.6em), line height
    width, x0, y0 = 760, 32, 80       # card width, text x, first baseline
    height = y0 + (len(TERMINAL_LINES) - 1) * lh + 34

    # ---- timeline (seconds) ----
    t = 0.7
    typed = []                        # (start, n_chars, dt)
    for kind, text in TERMINAL_LINES:
        s = ("$ " + text) if kind == "cmd" else text
        dt = 0.065 if kind == "cmd" else 0.022
        typed.append((t, s, dt))
        t += len(s) * dt + (0.35 if kind == "cmd" else 0.5)
    total = t - 0.5                   # moment the last character lands

    defs, body = [], []
    for i, (start, s, dt) in enumerate(typed):
        y = y0 + i * lh
        full = round(len(s) * cw, 1)
        # discrete keyframes: width 0 until `start`, then +1 char every dt
        vals = [0] + [round(k * cw, 1) for k in range(1, len(s) + 1)]
        keys = [0.0] + [(start + (k - 1) * dt) / total for k in range(1, len(s) + 1)]
        keys = [min(k, 1.0) for k in keys]
        defs.append(
            f'<clipPath id="c{i}"><rect x="{x0}" y="{y - 19}" width="{full}" height="26">'
            f'<animate attributeName="width" begin="0s" dur="{total:.2f}s" fill="freeze" '
            f'calcMode="discrete" values="{";".join(str(v) for v in vals)}" '
            f'keyTimes="{";".join(f"{k:.4f}" for k in keys)}"/></rect></clipPath>'
        )
        kind = TERMINAL_LINES[i][0]
        if kind == "cmd":
            rest = escape(s[2:])
            inner = (f'<tspan fill="{AMBER}">$ </tspan>'
                     f'<tspan fill="{TEXT}">{rest}</tspan>')
        else:
            inner = f'<tspan fill="{SKY}">{escape(s)}</tspan>'
        body.append(
            f'<text x="{x0}" y="{y}" clip-path="url(#c{i})" '
            f'xml:space="preserve">{inner}</text>'
        )

    last_y = y0 + (len(TERMINAL_LINES) - 1) * lh
    cur_x = x0 + len(typed[-1][1]) * cw + 5
    cursor = (
        f'<rect x="{cur_x:.1f}" y="{last_y - 14}" width="9" height="18" fill="{AMBER}" opacity="0">'
        f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" '
        f'begin="{total:.2f}s" repeatCount="indefinite"/></rect>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Terminal: Hitanshu Kanabar, Full Stack Developer, B.Tech IT, open to opportunities">
  <defs>
    <linearGradient id="win" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG_MID}"/>
      <stop offset="1" stop-color="{BG_DEEP}"/>
    </linearGradient>
    {"".join(defs)}
  </defs>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="url(#win)" stroke="{BORDER}"/>
  <path d="M0.5 40 V12.5 a12 12 0 0 1 12 -12 H{width - 12.5} a12 12 0 0 1 12 12 V40 Z" fill="{BORDER}" fill-opacity="0.55"/>
  <circle cx="24" cy="20" r="6" fill="#ff5f57"/>
  <circle cx="46" cy="20" r="6" fill="#febc2e"/>
  <circle cx="68" cy="20" r="6" fill="#28c840"/>
  <text x="{width / 2}" y="25" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{MUTED}">hitanshu@dev: ~/profile</text>
  <g font-family="{MONO}" font-size="{fs}">
    {"".join(body)}
    {cursor}
  </g>
</svg>
'''


def build_skills() -> str:
    width, pad = 760, 32
    label_x, track_x, track_w = pad, 250, 380
    row_h, top = 42, 30
    height = top + len(SKILLS) * row_h + 14
    fill_dur, stagger = 1.1, 0.14
    total = fill_dur + stagger * (len(SKILLS) - 1)

    rows = []
    for i, (name, pct, word) in enumerate(SKILLS):
        y = top + i * row_h
        target = round(track_w * pct / 100, 1)
        delay = 0.3 + i * stagger
        d = min(delay / (total + 0.3), 0.99)
        rows.append(f'''  <text x="{label_x}" y="{y + 14}" font-family="{SANS}" font-size="15" fill="{TEXT}">{escape(name)}</text>
  <rect x="{track_x}" y="{y + 2}" width="{track_w}" height="16" rx="8" fill="{BG_MID}" stroke="{BORDER}"/>
  <rect x="{track_x}" y="{y + 2}" width="{target}" height="16" rx="8" fill="url(#bar)">
    <animate attributeName="width" begin="0s" dur="{total + 0.3:.2f}s" fill="freeze" calcMode="spline"
      values="0;0;{target}" keyTimes="0;{d:.4f};1" keySplines="0 0 1 1;0.2 0.8 0.2 1"/>
  </rect>
  <text x="{track_x + track_w + 22}" y="{y + 15}" font-family="{SANS}" font-size="13" fill="{MUTED}">{escape(word)}</text>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Skill levels">
  <defs>
    <linearGradient id="card" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG_DEEP}"/>
      <stop offset="1" stop-color="{BG_MID}"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{AMBER}"/>
      <stop offset="1" stop-color="{SKY}"/>
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="url(#card)" stroke="{BORDER}"/>
{chr(10).join(rows)}
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "terminal.svg").write_text(build_terminal(), encoding="utf-8")
    (OUT / "skills.svg").write_text(build_skills(), encoding="utf-8")
    print("wrote", OUT / "terminal.svg")
    print("wrote", OUT / "skills.svg")
