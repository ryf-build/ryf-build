#!/usr/bin/env python3
import datetime as dt
import html
import json
import math
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "generated"
DATA = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)
DATA.mkdir(exist_ok=True)

USER = os.getenv("GITHUB_REPOSITORY_OWNER", "ryf-build")
TOKEN = os.getenv("GITHUB_TOKEN", "")
NOW = dt.datetime.now(dt.timezone.utc)

C = {
    "bg": "#07090d",
    "panel": "#0b0f14",
    "border": "#242a32",
    "text": "#f4f7fb",
    "sub": "#b7bec8",
    "muted": "#6f7782",
    "grid": "#1c232b",
    "gold": "#d8b86a",
    "gold2": "#f2d58b",
    "purple": "#9b87ff",
    "purple2": "#c4b5fd",
    "green": "#48e59b",
    "blue": "#58a6ff",
}

def esc(value):
    return html.escape(str(value), quote=True)

def api(url):
    headers = {
        "User-Agent": "ryf-profile",
        "Accept": "application/vnd.github+json",
    }
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    request = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(request, timeout=20).read())

def load_public():
    user = api(f"https://api.github.com/users/{USER}")
    repos_raw = api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
    events_raw = api(f"https://api.github.com/users/{USER}/events/public?per_page=30")

    repos = []
    for repo in repos_raw:
        if repo.get("fork"):
            continue
        repos.append({
            "name": repo.get("name", ""),
            "description": repo.get("description") or "",
            "language": repo.get("language") or "",
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "pushed_at": repo.get("pushed_at", ""),
        })

    events = []
    for event in events_raw:
        events.append({
            "type": event.get("type", "Event"),
            "repo": event.get("repo", {}).get("name", "").split("/")[-1],
            "created_at": event.get("created_at", ""),
        })

    return {
        "user": {
            "login": user.get("login", USER),
            "name": user.get("name") or "Ryf",
            "bio": user.get("bio") or "",
            "public_repos": user.get("public_repos", 0),
        },
        "repos": repos,
        "events": events,
        "generated_at": NOW.isoformat(),
    }

def svg_shell(body, width, height, title):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<title>{esc(title)}</title>
<defs>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['gold']}"/>
    <stop offset=".55" stop-color="{C['gold2']}"/>
    <stop offset="1" stop-color="{C['gold']}"/>
  </linearGradient>
  <linearGradient id="violet" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{C['purple2']}"/>
    <stop offset="1" stop-color="{C['purple']}"/>
  </linearGradient>
  <linearGradient id="system" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['purple']}"/>
    <stop offset=".5" stop-color="{C['gold']}"/>
    <stop offset="1" stop-color="{C['green']}"/>
  </linearGradient>
  <radialGradient id="glow">
    <stop offset="0" stop-color="{C['gold2']}" stop-opacity=".18"/>
    <stop offset=".55" stop-color="{C['purple']}" stop-opacity=".06"/>
    <stop offset="1" stop-color="{C['bg']}" stop-opacity="0"/>
  </radialGradient>
  <filter id="blur" x="-300%" y="-300%" width="600%" height="600%">
    <feGaussianBlur stdDeviation="7"/>
  </filter>
  <filter id="soft" x="-300%" y="-300%" width="600%" height="600%">
    <feGaussianBlur stdDeviation="3"/>
  </filter>
</defs>
<rect width="{width}" height="{height}" rx="28" fill="{C['bg']}"/>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="27" fill="none" stroke="{C['border']}"/>
{body}
</svg>"""


def hero(profile):
    updated = NOW.strftime("%Y-%m-%d %H:%M UTC")
    latest = next((r["name"] for r in profile["repos"] if r["name"] != USER), "public-work")

    # Perspective chessboard.
    board = []
    vx, vy = 884, 192
    left, right, top, bottom = 620, 1092, 270, 455
    files = 8
    ranks = 5
    for r in range(ranks):
        p0 = r / ranks
        p1 = (r + 1) / ranks
        y0 = top + (bottom - top) * (p0 ** 1.45)
        y1 = top + (bottom - top) * (p1 ** 1.45)
        xl0 = vx + (left - vx) * ((y0 - vy) / (bottom - vy))
        xr0 = vx + (right - vx) * ((y0 - vy) / (bottom - vy))
        xl1 = vx + (left - vx) * ((y1 - vy) / (bottom - vy))
        xr1 = vx + (right - vx) * ((y1 - vy) / (bottom - vy))
        for c in range(files):
            a0 = c / files
            a1 = (c + 1) / files
            x00 = xl0 + (xr0 - xl0) * a0
            x01 = xl0 + (xr0 - xl0) * a1
            x10 = xl1 + (xr1 - xl1) * a0
            x11 = xl1 + (xr1 - xl1) * a1
            fill = "#15120d" if (r + c) % 2 == 0 else "#090b0f"
            board.append(
                f'<polygon points="{x00:.1f},{y0:.1f} {x01:.1f},{y0:.1f} {x11:.1f},{y1:.1f} {x10:.1f},{y1:.1f}" '
                f'fill="{fill}" stroke="#2a2418" stroke-width=".55" opacity=".94"/>'
            )

    # Architectural background and bokeh.
    columns = []
    for i in range(8):
        x = 628 + i * 54
        op = .13 if i % 2 == 0 else .07
        columns.append(
            f'<rect x="{x}" y="55" width="13" height="250" fill="#cda85a" opacity="{op}"/>'
            f'<rect x="{x+16}" y="55" width="2" height="250" fill="#d8b86a" opacity=".08"/>'
        )
    bokeh = []
    for i in range(26):
        x = 610 + ((i * 83) % 470)
        y = 72 + ((i * 47) % 255)
        r = 1.2 + (i % 4) * .85
        color = "#f2d58b" if i % 3 != 0 else "#9b87ff"
        dur = 2.4 + (i % 6) * .47
        bokeh.append(
            f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{color}" opacity=".22">'
            f'<animate attributeName="opacity" values=".08;.75;.08" dur="{dur:.2f}s" begin="-{i*.13:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    # Knight silhouette behind the king.
    knight = """
    <g opacity=".82">
      <path d="M690 310
               C706 288 721 268 736 251
               C724 232 720 214 727 196
               C735 178 753 166 769 149
               L755 121
               L789 135
               C816 145 835 166 838 192
               C823 187 811 183 799 183
               C804 197 805 212 800 225
               C789 251 764 274 744 294
               L760 310 Z"
            fill="#0b0e12" stroke="#7f6a3e" stroke-width="2.4"/>
      <path d="M727 196 C754 177 785 165 812 173"
            fill="none" stroke="#d8b86a" stroke-width="1.4" opacity=".45"/>
      <circle cx="785" cy="164" r="3.2" fill="#f2d58b" opacity=".75"/>
      <path d="M684 311 Q726 298 769 311 L783 342 H671 Z"
            fill="#090b0f" stroke="#50432b" stroke-width="2"/>
      <path d="M686 319 Q728 307 777 320" fill="none" stroke="#d8b86a" stroke-width="1" opacity=".3"/>
    </g>
    """

    # Detailed king: layered fill, outline, wireframe, particles.
    king_paths = """
    <g>
      <path d="M904 55 L904 89 M888 72 H920"
            stroke="#f2d58b" stroke-width="6" stroke-linecap="round"/>
      <path d="M876 98
               C883 88 893 83 904 83
               C915 83 925 88 932 98
               L925 115
               C920 123 914 128 904 128
               C894 128 888 123 883 115 Z"
            fill="url(#kingGold)" stroke="#f2d58b" stroke-width="2.5"/>
      <path d="M878 130 Q904 142 930 130 L923 151 Q904 161 885 151 Z"
            fill="#18140d" stroke="#d8b86a" stroke-width="2"/>
      <path d="M887 157
               C884 187 879 216 864 247
               C850 277 831 306 818 327
               H990
               C977 306 958 277 944 247
               C929 216 924 187 921 157 Z"
            fill="url(#kingBody)" stroke="#f2d58b" stroke-width="2.8"/>
      <path d="M818 327 Q904 307 990 327 L982 348 Q904 332 826 348 Z"
            fill="#15110b" stroke="#d8b86a" stroke-width="2.3"/>
      <path d="M808 350 Q904 331 1000 350 L989 377 H819 Z"
            fill="url(#kingBase)" stroke="#f2d58b" stroke-width="2.8"/>
      <path d="M819 364 Q904 348 989 364"
            fill="none" stroke="#f2d58b" stroke-width="1.3" opacity=".5"/>
    </g>
    """

    wire = []
    for i in range(10):
        y = 168 + i * 17
        half = 20 + i * 8.3
        wire.append(
            f'<path d="M{904-half:.1f} {y} Q904 {y-10:.1f} {904+half:.1f} {y}" '
            f'fill="none" stroke="#d8b86a" stroke-width=".8" opacity="{.18 + i*.018:.2f}"/>'
        )
    for i in range(7):
        x = 850 + i * 18
        wire.append(
            f'<path d="M904 158 C{x} 220 {x-30} 286 {x-42} 331" '
            f'fill="none" stroke="#f2d58b" stroke-width=".65" opacity=".18"/>'
        )
        wire.append(
            f'<path d="M904 158 C{958-(x-850)} 220 {988-(x-850)} 286 {1000-(x-850)} 331" '
            f'fill="none" stroke="#f2d58b" stroke-width=".65" opacity=".18"/>'
        )

    particles = []
    for i in range(86):
        # deterministic points distributed around king body
        y = 105 + ((i * 37) % 238)
        p = min(1, max(0, (y - 150) / 185))
        half = 22 + 75 * (p ** 1.35)
        side = -1 if i % 2 == 0 else 1
        x = 904 + side * (half * (.22 + ((i * 29) % 73) / 100))
        color = "#f2d58b" if i % 5 < 4 else "#9b87ff"
        rr = 1.0 + (i % 4) * .35
        particles.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.2f}" fill="{color}" opacity=".45">'
            f'<animate attributeName="opacity" values=".12;.9;.12" dur="{2.2+(i%7)*.33:.2f}s" begin="-{i*.08:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    orbit_svg = []
    orbit_specs = [
        (905, 211, 182, 52, 6, 19, "#d8b86a", 1),
        (905, 211, 162, 70, 44, 25, "#9b87ff", -1),
        (905, 211, 139, 87, 79, 31, "#48e59b", 1),
    ]
    for cx,cy,rx,ry,angle,dur,color,direction in orbit_specs:
        end = angle + direction * 360
        orbit_svg.append(
            f'<g transform="rotate({angle} {cx} {cy})">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{color}" stroke-width="1.15" opacity=".28"/>'
            f'<circle cx="{cx+rx}" cy="{cy}" r="3.7" fill="{color}" filter="url(#softGlow)"/>'
            f'<animateTransform attributeName="transform" type="rotate" values="{angle} {cx} {cy};{end} {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/>'
            f'</g>'
        )

    pills = ["AI Agents","Automation","Infrastructure","Verification","Open Source","AI Workflows","Windows","Systems"]
    pill_svg = []
    for i, label in enumerate(pills):
        row, col = divmod(i, 4)
        x = 52 + col * 132
        y = 302 + row * 40
        pill_svg.append(
            f'<rect x="{x}" y="{y}" width="118" height="28" rx="14" fill="#090c10" stroke="#8f7745" stroke-width="1"/>'
            f'<text x="{x+59}" y="{y+18.5}" text-anchor="middle" fill="#c9d1d9" font-size="10" font-family="Segoe UI">{label}</text>'
        )

    coords = []
    for i, ch in enumerate("ABCDEFGH"):
        coords.append(f'<text x="{680+i*47}" y="446" fill="#6f7782" font-size="9.5" font-family="monospace">{ch}</text>')
    for i in range(8):
        coords.append(f'<text x="1080" y="{88+i*41}" fill="#5d5546" font-size="9" font-family="monospace">A{i+1}</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="482" viewBox="0 0 1120 482" role="img">
<title>RYF chess strategy hero</title>
<defs>
  <linearGradient id="heroBg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#07090d"/>
    <stop offset=".58" stop-color="#090b0f"/>
    <stop offset="1" stop-color="#0b0d10"/>
  </linearGradient>
  <linearGradient id="kingGold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f4dc99"/>
    <stop offset=".35" stop-color="#9b7430"/>
    <stop offset=".7" stop-color="#20170b"/>
    <stop offset="1" stop-color="#e0b75e"/>
  </linearGradient>
  <linearGradient id="kingBody" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#0b0d11"/>
    <stop offset=".38" stop-color="#1b160d"/>
    <stop offset=".55" stop-color="#4c3514"/>
    <stop offset=".74" stop-color="#16120b"/>
    <stop offset="1" stop-color="#080a0d"/>
  </linearGradient>
  <linearGradient id="kingBase" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#090b0f"/>
    <stop offset=".5" stop-color="#34240f"/>
    <stop offset="1" stop-color="#090b0f"/>
  </linearGradient>
  <radialGradient id="kingGlow">
    <stop offset="0" stop-color="#f2d58b" stop-opacity=".24"/>
    <stop offset=".45" stop-color="#d8b86a" stop-opacity=".08"/>
    <stop offset="1" stop-color="#07090d" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#f2d58b" stop-opacity="0"/>
    <stop offset=".5" stop-color="#f2d58b" stop-opacity=".12"/>
    <stop offset="1" stop-color="#f2d58b" stop-opacity="0"/>
  </linearGradient>
  <filter id="softGlow" x="-300%" y="-300%" width="600%" height="600%">
    <feGaussianBlur stdDeviation="3"/>
  </filter>
  <filter id="bigGlow" x="-300%" y="-300%" width="600%" height="600%">
    <feGaussianBlur stdDeviation="12"/>
  </filter>
</defs>

<rect width="1120" height="482" rx="28" fill="url(#heroBg)"/>
<rect x="1" y="1" width="1118" height="480" rx="27" fill="none" stroke="#25292f"/>

<g>{''.join(columns)}</g>
<g>{''.join(bokeh)}</g>

<!-- left editorial block -->
<text x="52" y="50" fill="#9b87ff" font-size="11" font-weight="700" font-family="monospace">ryf-build / README.md</text>
<text x="52" y="133" fill="#fff1c5" font-size="76" font-weight="800" font-family="Georgia, serif" letter-spacing="2.5">RYF</text>
<text x="54" y="176" fill="#f2d58b" font-size="21.5" font-weight="700" font-family="Georgia, serif" letter-spacing="1.05">AI-NATIVE PRODUCT BUILDER</text>
<text x="54" y="211" fill="#f4f7fb" font-size="16.5" font-family="Georgia, serif" letter-spacing="2.1">STRATEGY · SYSTEMS · EXECUTION</text>
<text x="54" y="247" fill="#c9d1d9" font-size="14.5" font-family="Segoe UI">Building software, automation, and engineering systems with AI.</text>
<text x="54" y="270" fill="#7d8590" font-size="11.8" font-family="Segoe UI">Make the move deliberate. Build the position. Verify the result.</text>
{''.join(pill_svg)}

<!-- right cinematic field -->
<circle cx="905" cy="210" r="215" fill="url(#kingGlow)"/>
<g opacity=".96">{''.join(board)}</g>
{knight}
{''.join(orbit_svg)}
{king_paths}
<g>{''.join(wire)}</g>
<g>{''.join(particles)}</g>

<!-- labels -->
<text x="650" y="70" fill="#f2d58b" font-size="10.5" font-weight="800" font-family="Georgia, serif" letter-spacing="1.6">STRATEGY</text>
<text x="650" y="86" fill="#a99463" font-size="9" font-family="Segoe UI" letter-spacing="1.1">BUILDS OPTIONS</text>
<text x="994" y="104" fill="#f2d58b" font-size="10.5" font-weight="800" font-family="Georgia, serif" letter-spacing="1.6">SYSTEMS</text>
<text x="994" y="120" fill="#a99463" font-size="9" font-family="Segoe UI" letter-spacing="1.1">CREATE LEVERAGE</text>
<text x="986" y="246" fill="#f2d58b" font-size="10.5" font-weight="800" font-family="Georgia, serif" letter-spacing="1.6">EXECUTION</text>
<text x="986" y="262" fill="#a99463" font-size="9" font-family="Segoe UI" letter-spacing="1.1">TURNS IDEAS</text>
<text x="986" y="276" fill="#a99463" font-size="9" font-family="Segoe UI" letter-spacing="1.1">INTO REALITY</text>

<g>{''.join(coords)}</g>

<!-- motion accents -->
<rect x="610" y="32" width="72" height="402" fill="url(#scan)" opacity=".62">
  <animate attributeName="x" values="610;1030;610" dur="8.2s" repeatCount="indefinite"/>
</rect>
<circle cx="665" cy="427" r="3.2" fill="#f2d58b">
  <animate attributeName="cx" values="665;1052;665" dur="6.2s" repeatCount="indefinite"/>
  <animate attributeName="fill" values="#f2d58b;#9b87ff;#48e59b;#f2d58b" dur="6.2s" repeatCount="indefinite"/>
</circle>

<text x="52" y="462" fill="#616975" font-size="9.2" font-family="monospace">latest public work / {esc(latest)} · animated profile · refreshed {updated}</text>
</svg>"""


def about(profile):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="180" viewBox="0 0 1120 180" role="img">
<title>RYF opening and about</title>
<rect width="1120" height="180" rx="22" fill="#07090d"/>
<rect x="1" y="1" width="1118" height="178" rx="21" fill="none" stroke="#242a32"/>
<text x="30" y="38" fill="#f2d58b" font-size="18" font-weight="700" font-family="Georgia, serif">♞  Opening / About</text>
<text x="30" y="76" fill="#f4f7fb" font-size="14.5" font-family="Segoe UI">I'm Ryf, an AI-native product builder.</text>
<text x="30" y="102" fill="#b7bec8" font-size="13.5" font-family="Segoe UI">I build software, automation, and engineering systems with AI.</text>
<text x="30" y="126" fill="#b7bec8" font-size="13.5" font-family="Segoe UI">Public repositories contain reusable tools and experiments; private product and production systems remain private.</text>
<text x="30" y="150" fill="#6f7782" font-size="12" font-family="Segoe UI">The goal: turn ideas into practical systems that improve development, operations, and everyday work.</text>
<line x1="824" y1="48" x2="824" y2="144" stroke="#d8b86a" stroke-width="2"/>
<text x="854" y="82" fill="#d8b86a" font-size="34" font-family="Georgia, serif">“</text>
<text x="872" y="97" fill="#f4f7fb" font-size="18" font-family="Georgia, serif">A better position</text>
<text x="872" y="124" fill="#f4f7fb" font-size="18" font-family="Georgia, serif">tomorrow.</text>
<text x="1043" y="146" fill="#d8b86a" font-size="34" font-family="Georgia, serif">”</text>
</svg>"""

def capability():

    cx, cy, radius = 280, 185, 112
    labels = [
        ("SYSTEM DESIGN", -90),
        ("AI WORKFLOWS", -30),
        ("AUTOMATION", 30),
        ("INFRASTRUCTURE", 90),
        ("QA / VERIFY", 150),
        ("PRODUCT ENG", 210),
    ]
    axes = []
    label_svg = []
    for text, deg in labels:
        rad = math.radians(deg)
        x = cx + math.cos(rad) * radius
        y = cy + math.sin(rad) * radius
        axes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{C["grid"]}" stroke-width="1"/>')
        lx = cx + math.cos(rad) * (radius + 30)
        ly = cy + math.sin(rad) * (radius + 30)
        anchor = "middle"
        if math.cos(rad) > .35: anchor = "start"
        if math.cos(rad) < -.35: anchor = "end"
        label_svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="{C["sub"]}" font-size="10.5" font-family="Segoe UI">{text}</text>'
        )

    rings = []
    for rr in (28, 56, 84, 112):
        pts = []
        for _, deg in labels:
            rad = math.radians(deg)
            pts.append(f"{cx+math.cos(rad)*rr:.1f},{cy+math.sin(rad)*rr:.1f}")
        rings.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{C["grid"]}" stroke-width=".8"/>')

    values = [1.00, .88, .94, .90, .92, .86]
    pts = []
    nodes = []
    for i, (_, deg) in enumerate(labels):
        rad = math.radians(deg)
        rr = radius * values[i]
        x = cx + math.cos(rad) * rr
        y = cy + math.sin(rad) * rr
        pts.append(f"{x:.1f},{y:.1f}")
        nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{C["gold2"]}">'
            f'<animate attributeName="r" values="3.2;5.8;3.2" dur="{2.4+i*.18:.2f}s" begin="-{i*.25:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    caps = [
        ("AI / AGENTS", "CORE", C["purple"]),
        ("NODE.JS", "CORE", C["green"]),
        ("POWERSHELL", "CORE", C["blue"]),
        ("AUTOMATION", "CORE", C["gold"]),
        ("INFRASTRUCTURE", "STRONG", C["green"]),
        ("DEVOPS", "STRONG", C["purple"]),
        ("QA / VERIFICATION", "CORE", C["gold"]),
        ("SYSTEMS", "CORE", C["blue"]),
    ]
    rows = []
    for i,(name,status,color) in enumerate(caps):
        y = 72 + i * 31
        width = 176 if status == "CORE" else 142
        rows.append(
            f'<text x="596" y="{y}" fill="{C["sub"]}" font-size="11.5" font-family="Segoe UI">{name}</text>'
            f'<rect x="760" y="{y-9}" width="210" height="8" rx="4" fill="#141b23"/>'
            f'<rect x="760" y="{y-9}" width="{width}" height="8" rx="4" fill="{color}" opacity=".78"/>'
            f'<rect x="760" y="{y-9}" width="30" height="8" rx="4" fill="{C["text"]}" opacity=".12">'
            f'<animate attributeName="x" values="760;{760+max(1,width-30)};760" dur="{3.8+i*.21:.2f}s" begin="-{i*.14:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
            f'<text x="988" y="{y}" fill="{color}" font-size="10" font-family="monospace">{status}</text>'
        )

    body = f"""
<text x="30" y="38" fill="{C['gold2']}" font-size="18" font-weight="700" font-family="Georgia, serif">♛  Board Control / Technical Capability</text>
<text x="30" y="59" fill="{C['muted']}" font-size="10.5" font-family="Segoe UI">Capability map — qualitative focus, not a score.</text>

{''.join(rings)}
{''.join(axes)}
<polygon points="{' '.join(pts)}" fill="{C['purple']}" fill-opacity=".18" stroke="url(#violet)" stroke-width="2.2">
  <animate attributeName="fill-opacity" values=".12;.28;.12" dur="4.5s" repeatCount="indefinite"/>
</polygon>
{''.join(nodes)}
{''.join(label_svg)}

<line x1="540" y1="54" x2="540" y2="316" stroke="{C['grid']}" stroke-width="1"/>
{''.join(rows)}
"""
    return svg_shell(body, 1120, 340, "RYF technical capability")

def toolchain():
    tools = [
        ("TS","TypeScript","Language",C["blue"]),
        ("NODE","Node.js","Runtime",C["green"]),
        ("PS","PowerShell","Automation",C["blue"]),
        ("GH","GitHub Actions","CI / CD",C["purple"]),
        ("WIN","Windows","Platform",C["blue"]),
        ("AI","AI Workflows","LLM / Agents",C["purple"]),
        ("OPS","DevOps","Infrastructure",C["green"]),
        ("QA","Verification","Review / Tests",C["gold"]),
    ]
    cards = []
    for i,(code,name,desc,color) in enumerate(tools):
        row, col = divmod(i,4)
        x = 30 + col * 268
        y = 72 + row * 86
        cards.append(
            f'<rect x="{x}" y="{y}" width="250" height="70" rx="14" fill="#0b1016" stroke="{C["border"]}"/>'
            f'<rect x="{x+1}" y="{y+1}" width="4" height="68" rx="2" fill="{color}" opacity=".72"/>'
            f'<rect x="{x+17}" y="{y+17}" width="42" height="36" rx="9" fill="#101720" stroke="{color}" stroke-opacity=".45"/>'
            f'<text x="{x+38}" y="{y+41}" text-anchor="middle" fill="{color}" font-size="11" font-weight="800" font-family="monospace">{code}</text>'
            f'<text x="{x+72}" y="{y+29}" fill="{C["text"]}" font-size="13" font-weight="700" font-family="Segoe UI">{name}</text>'
            f'<text x="{x+72}" y="{y+49}" fill="{C["muted"]}" font-size="10.5" font-family="Segoe UI">{desc}</text>'
            f'<rect x="{x+8}" y="{y+3}" width="54" height="1" fill="{color}" opacity=".2">'
            f'<animate attributeName="x" values="{x+8};{x+188};{x+8}" dur="{4.1+(i%4)*.38:.2f}s" begin="-{i*.1:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )
    body = f"""
<text x="30" y="38" fill="{C['gold2']}" font-size="18" font-weight="700" font-family="Georgia, serif">♞  Pieces / Core Toolchain</text>
{''.join(cards)}
"""
    return svg_shell(body, 1120, 250, "RYF core toolchain")

def signals(profile):
    public_repos = profile["user"]["public_repos"]
    experiments = max(0, len([r for r in profile["repos"] if r["name"] != USER]))
    signals = [
        ("PUBLIC REPOS", str(public_repos), "Open public surface", C["green"]),
        ("AUTOMATION", "ACTIVE", "6-hour profile refresh", C["purple"]),
        ("PUBLIC EXPERIMENTS", str(experiments), "Reusable ideas + tools", C["gold"]),
        ("WRITING", "1", "Practical engineering", C["blue"]),
        ("VERIFICATION", "BUILT IN", "Review · test · evidence", C["green"]),
    ]
    cards = []
    for i,(label,value,desc,color) in enumerate(signals):
        x = 30 + i * 214
        cards.append(
            f'<rect x="{x}" y="68" width="196" height="118" rx="14" fill="#0b1016" stroke="{C["border"]}"/>'
            f'<circle cx="{x+20}" cy="90" r="4" fill="{color}"><animate attributeName="opacity" values=".3;1;.3" dur="{2.2+i*.34:.2f}s" repeatCount="indefinite"/></circle>'
            f'<text x="{x+34}" y="94" fill="{C["muted"]}" font-size="9.5" font-family="Segoe UI" letter-spacing=".9">{label}</text>'
            f'<text x="{x+18}" y="134" fill="{C["text"]}" font-size="25" font-weight="800" font-family="Segoe UI">{value}</text>'
            f'<text x="{x+18}" y="163" fill="{C["sub"]}" font-size="10.2" font-family="Segoe UI">{desc}</text>'
        )
    body = f"""
<text x="30" y="38" fill="{C['gold2']}" font-size="18" font-weight="700" font-family="Georgia, serif">♜  Middle Game / Engineering Signals</text>
{''.join(cards)}
"""
    return svg_shell(body, 1120, 210, "RYF engineering signals")

def project_card(name, description, tags, accent):
    tags_svg = []
    x = 18
    for tag in tags[:3]:
        w = 18 + len(tag) * 6.3
        tags_svg.append(
            f'<rect x="{x}" y="144" width="{w:.1f}" height="25" rx="12.5" fill="#111720" stroke="{C["border"]}"/>'
            f'<text x="{x+w/2:.1f}" y="161" text-anchor="middle" fill="{C["muted"]}" font-size="9.5" font-family="Segoe UI">{esc(tag)}</text>'
        )
        x += w + 8
    desc1 = description[:58]
    desc2 = description[58:116]
    return svg_shell(f"""
<text x="18" y="31" fill="{accent}" font-size="10.5" font-weight="800" font-family="monospace">SELECTED LINE / PUBLIC</text>
<text x="18" y="66" fill="{C['text']}" font-size="17" font-weight="800" font-family="Segoe UI">{esc(name)}</text>
<text x="18" y="97" fill="{C['sub']}" font-size="11" font-family="Segoe UI">{esc(desc1)}</text>
<text x="18" y="115" fill="{C['sub']}" font-size="11" font-family="Segoe UI">{esc(desc2)}</text>
{''.join(tags_svg)}
<circle cx="320" cy="30" r="4" fill="{accent}">
  <animate attributeName="r" values="3;6;3" dur="2.6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".35;1;.35" dur="2.6s" repeatCount="indefinite"/>
</circle>
""", 350, 190, name)

def projects(profile):
    by_name = {r["name"]: r for r in profile["repos"]}
    specs = [
        ("windows-ai-dev-team", ["Windows","PowerShell","Automation"], C["gold"]),
        ("ai-development-playbook", ["AI","Docs","Development"], C["purple"]),
        ("ryf-labs", ["Experiments","AI","Tools"], C["green"]),
    ]
    out = {}
    for name,tags,accent in specs:
        repo = by_name.get(name, {"description": name})
        out[name] = project_card(name, repo.get("description") or name, tags, accent)
    return out

def writing():
    squares = []
    x0, y0, s = 18, 38, 22
    for r in range(5):
        for c in range(8):
            fill = "#15120c" if (r+c)%2==0 else "#0d0f12"
            squares.append(f'<rect x="{x0+c*s}" y="{y0+r*s}" width="{s}" height="{s}" fill="{fill}"/>')
    pieces = [
        (40,112,"♟"),(65,90,"♙"),(92,112,"♞"),(122,83,"♛"),(154,106,"♜")
    ]
    pcs = ''.join(f'<text x="{x}" y="{y}" fill="{C["gold2"]}" font-size="32" font-family="Georgia, serif" opacity=".9">{p}</text>' for x,y,p in pieces)
    body = f"""
<g opacity=".88">{''.join(squares)}</g>
{pcs}
<rect x="-110" y="24" width="100" height="128" fill="{C['gold2']}" opacity=".08">
  <animate attributeName="x" values="-110;210;-110" dur="5.2s" repeatCount="indefinite"/>
</rect>
<line x1="220" y1="24" x2="220" y2="154" stroke="{C['grid']}"/>
<text x="252" y="45" fill="{C['gold2']}" font-size="10.5" font-weight="800" font-family="monospace">ENDGAME / WRITING</text>
<text x="252" y="83" fill="{C['text']}" font-size="24" font-weight="800" font-family="Segoe UI">1台のWindows PCをAI開発チームにする</text>
<text x="252" y="111" fill="{C['sub']}" font-size="12.5" font-family="Segoe UI">GitHub · self-hosted runners · automation · QA · human-controlled AI workflows</text>
<text x="252" y="139" fill="{C['muted']}" font-size="10.5" font-family="Segoe UI">Practical engineering guide / companion: windows-ai-dev-team</text>
"""
    return svg_shell(body, 1120, 180, "RYF writing")

def main():
    profile = load_public()

    for path in OUT.glob("*.svg"):
        path.unlink()

    (OUT / "hero.svg").write_text(hero(profile), encoding="utf-8")
    (OUT / "about.svg").write_text(about(profile), encoding="utf-8")
    (OUT / "capability.svg").write_text(capability(), encoding="utf-8")
    (OUT / "toolchain.svg").write_text(toolchain(), encoding="utf-8")
    (OUT / "signals.svg").write_text(signals(profile), encoding="utf-8")
    for name, content in projects(profile).items():
        (OUT / f"project-{name}.svg").write_text(content, encoding="utf-8")
    (OUT / "writing.svg").write_text(writing(), encoding="utf-8")

    snapshot = {
        "user": profile["user"],
        "repos": profile["repos"],
        "events": profile["events"],
        "generated_at": profile["generated_at"],
        "scope": "public-only",
    }
    (DATA / "snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
