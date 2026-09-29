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

COLORS = {
    "bg": "#07090d",
    "panel": "#0b0f14",
    "border": "#20262e",
    "text": "#f4f7fb",
    "sub": "#aab4c0",
    "muted": "#66707c",
    "grid": "#1a222b",
    "violet": "#9b87ff",
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
        },
        "repos": repos,
        "events": events,
        "generated_at": NOW.isoformat(),
    }

def latest_public_work(profile):
    for repo in profile["repos"]:
        if repo["name"] != USER:
            return repo["name"]
    return "public-work"

def orbital_group(cx, cy, rx, ry, angle, duration, direction, color, seed):
    dots = []
    for i in range(14):
        t = 2 * math.pi * i / 14
        x = cx + rx * math.cos(t)
        y = cy + ry * math.sin(t)
        r = 1.4 + ((i + seed) % 4) * 0.45
        opacity = 0.26 + ((i * 3 + seed) % 5) * 0.11
        dots.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{color}" opacity="{opacity:.2f}">'
            f'<animate attributeName="opacity" values="{max(.18, opacity-.15):.2f};{min(.96, opacity+.28):.2f};{max(.18, opacity-.15):.2f}" dur="{2.5+(i%5)*.42:.2f}s" begin="-{i*.09:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    end = angle + (360 if direction > 0 else -360)
    return (
        f'<g transform="rotate({angle} {cx} {cy})">'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{color}" stroke-width=".8" opacity=".18"/>'
        + ''.join(dots) +
        f'<animateTransform attributeName="transform" type="rotate" values="{angle} {cx} {cy};{end} {cx} {cy}" dur="{duration}s" repeatCount="indefinite"/>'
        f'</g>'
    )

def interface(profile):
    latest = latest_public_work(profile)
    cx, cy = 885, 206

    grid = []
    for x in range(654, 1110, 32):
        grid.append(f'<line x1="{x}" y1="56" x2="{x}" y2="354" stroke="{COLORS["grid"]}" stroke-width=".65" opacity=".55"/>')
    for y in range(66, 355, 32):
        grid.append(f'<line x1="650" y1="{y}" x2="1110" y2="{y}" stroke="{COLORS["grid"]}" stroke-width=".65" opacity=".55"/>')

    orbitals = [
        orbital_group(cx, cy, 178, 42, 8, 28, 1, COLORS["violet"], 1),
        orbital_group(cx, cy, 162, 55, 42, 34, -1, COLORS["green"], 2),
        orbital_group(cx, cy, 148, 68, 78, 31, 1, COLORS["blue"], 3),
        orbital_group(cx, cy, 134, 38, 118, 26, -1, COLORS["violet"], 4),
        orbital_group(cx, cy, 120, 74, 154, 36, 1, COLORS["green"], 5),
    ]

    event_nodes = []
    event_colors = {
        "PushEvent": COLORS["green"],
        "PullRequestEvent": COLORS["violet"],
        "IssuesEvent": COLORS["blue"],
        "CreateEvent": "#d1d5db",
        "IssueCommentEvent": "#aab4c0",
    }
    for i, event in enumerate(profile["events"][:7]):
        theta = (i * 0.88) + 0.45
        x = cx + math.cos(theta) * (78 + (i % 3) * 22)
        y = cy + math.sin(theta) * (52 + (i % 2) * 18)
        color = event_colors.get(event["type"], COLORS["blue"])
        event_nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}" filter="url(#glow)">'
            f'<animate attributeName="r" values="2.4;6.2;2.4" dur="{2.1+i*.24:.2f}s" begin="-{i*.22:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".45;1;.45" dur="{2.1+i*.24:.2f}s" begin="-{i*.22:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    latest_repo = esc(latest)
    updated = NOW.strftime("%Y-%m-%d %H:%M UTC")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="410" viewBox="0 0 1120 410" role="img">
<title>RYF — AI-native product builder</title>
<defs>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{COLORS['violet']}"/>
    <stop offset="1" stop-color="{COLORS['green']}"/>
  </linearGradient>
  <radialGradient id="orbGlow">
    <stop offset="0" stop-color="{COLORS['violet']}" stop-opacity=".13"/>
    <stop offset=".48" stop-color="{COLORS['green']}" stop-opacity=".06"/>
    <stop offset="1" stop-color="{COLORS['bg']}" stop-opacity="0"/>
  </radialGradient>
  <filter id="glow" x="-300%" y="-300%" width="600%" height="600%">
    <feGaussianBlur stdDeviation="5"/>
  </filter>
</defs>

<rect width="1120" height="410" rx="28" fill="{COLORS['bg']}"/>
<rect x="1" y="1" width="1118" height="408" rx="27" fill="none" stroke="{COLORS['border']}"/>

<text x="54" y="54" fill="{COLORS['muted']}" font-size="11" font-weight="700" font-family="Segoe UI, Inter, Arial, sans-serif" letter-spacing="2.6">RYF / LIVE PROFILE SYSTEM</text>

<text x="52" y="128" fill="{COLORS['text']}" font-size="59" font-weight="820" font-family="Segoe UI, Inter, Arial, sans-serif" letter-spacing=".5">AI-NATIVE</text>
<text x="52" y="185" fill="{COLORS['text']}" font-size="59" font-weight="820" font-family="Segoe UI, Inter, Arial, sans-serif" letter-spacing=".5">PRODUCT BUILDER</text>
<rect x="54" y="211" width="338" height="3" rx="1.5" fill="url(#accent)"/>

<text x="54" y="254" fill="{COLORS['sub']}" font-size="18" font-family="Segoe UI, Inter, Arial, sans-serif">Software · automation · infrastructure · AI</text>
<text x="54" y="292" fill="{COLORS['muted']}" font-size="12.5" font-family="Segoe UI, Inter, Arial, sans-serif" letter-spacing="1.2">BUILD DELIBERATELY · VERIFY WHAT MATTERS</text>

<circle cx="58" cy="335" r="4" fill="{COLORS['green']}">
  <animate attributeName="opacity" values=".35;1;.35" dur="2.2s" repeatCount="indefinite"/>
</circle>
<text x="72" y="340" fill="{COLORS['sub']}" font-size="12.5" font-family="Segoe UI, Inter, Arial, sans-serif">PUBLIC PROFILE LIVE</text>
<text x="230" y="340" fill="{COLORS['muted']}" font-size="12.5" font-family="Segoe UI, Inter, Arial, sans-serif">·</text>
<text x="248" y="340" fill="{COLORS['sub']}" font-size="12.5" font-family="Segoe UI, Inter, Arial, sans-serif">AUTOMATION / 6H</text>
<text x="374" y="340" fill="{COLORS['muted']}" font-size="12.5" font-family="Segoe UI, Inter, Arial, sans-serif">·</text>
<text x="392" y="340" fill="{COLORS['sub']}" font-size="12.5" font-family="Segoe UI, Inter, Arial, sans-serif">PRIVATE / SEALED</text>

<text x="54" y="376" fill="{COLORS['muted']}" font-size="10.5" font-family="monospace">latest public work / {latest_repo}</text>

<g opacity=".72">{''.join(grid)}</g>
<circle cx="{cx}" cy="{cy}" r="205" fill="url(#orbGlow)"/>

{''.join(orbitals)}

<circle cx="{cx}" cy="{cy}" r="5" fill="{COLORS['text']}"/>
<circle cx="{cx}" cy="{cy}" r="20" fill="none" stroke="{COLORS['border']}" opacity=".9"/>
<circle cx="{cx}" cy="{cy}" r="36" fill="none" stroke="{COLORS['border']}" opacity=".55"/>

{''.join(event_nodes)}

<line x1="676" y1="66" x2="676" y2="350" stroke="{COLORS['green']}" stroke-width="1.1" opacity=".22">
  <animate attributeName="x1" values="676;1092;676" dur="5.8s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="676;1092;676" dur="5.8s" repeatCount="indefinite"/>
</line>

<path d="M672 326H1088" stroke="{COLORS['border']}" stroke-width="1"/>
<circle cx="688" cy="326" r="3.2" fill="{COLORS['green']}">
  <animate attributeName="cx" values="688;1072;688" dur="6.6s" repeatCount="indefinite"/>
  <animate attributeName="fill" values="{COLORS['violet']};{COLORS['green']};{COLORS['blue']};{COLORS['violet']}" dur="6.6s" repeatCount="indefinite"/>
</circle>

<text x="672" y="370" fill="{COLORS['muted']}" font-size="9.5" font-family="monospace">public event field / refreshed {updated}</text>
</svg>"""

def main():
    profile = load_public()

    for path in OUT.glob("*.svg"):
        path.unlink()

    (OUT / "interface.svg").write_text(interface(profile), encoding="utf-8")

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
