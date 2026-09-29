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
    "gold": "#e3bd62",
    "purple": "#a78bfa",
    "green": "#63e6a1",
    "blue": "#58a6ff",
    "bg": "#080a0e",
    "panel": "#0d1117",
    "border": "#21262d",
    "text": "#f0f6fc",
    "sub": "#c9d1d9",
    "muted": "#7d8590",
    "grid": "#27303a",
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

def shell(body, width, height, title):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<title>{esc(title)}</title>
<defs>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['gold']}"/>
    <stop offset=".52" stop-color="{C['purple']}"/>
    <stop offset="1" stop-color="{C['green']}"/>
  </linearGradient>
  <radialGradient id="radarGlow">
    <stop offset="0" stop-color="{C['green']}" stop-opacity=".20"/>
    <stop offset="1" stop-color="{C['green']}" stop-opacity="0"/>
  </radialGradient>
  <filter id="glow" x="-300%" y="-300%" width="600%" height="600%">
    <feGaussianBlur stdDeviation="4"/>
  </filter>
</defs>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="26" fill="{C['bg']}" stroke="{C['border']}"/>
{body}
</svg>"""

def hud(profile):
    repos = profile["repos"]
    top = repos[0]["name"] if repos else "ryf-build"

    status = [
        ("SYSTEM", "LIVE", C["green"]),
        ("PUBLIC", "OPEN", C["gold"]),
        ("PRIVATE", "SEALED", C["purple"]),
        ("AUTOMATION", "ACTIVE", C["blue"]),
    ]
    status_svg = []
    for i, (label, value, color) in enumerate(status):
        x = 42 + i * 145
        status_svg.append(
            f'<text x="{x}" y="211" fill="{C["muted"]}" font-size="10.5" font-family="Segoe UI" letter-spacing="1.2">{label}</text>'
            f'<circle cx="{x+3}" cy="239" r="4" fill="{color}"><animate attributeName="opacity" values=".35;1;.35" dur="{2.2+i*.45}s" repeatCount="indefinite"/></circle>'
            f'<text x="{x+16}" y="244" fill="{C["text"]}" font-size="21" font-weight="700" font-family="Segoe UI">{value}</text>'
        )

    pulse_bars = []
    for i in range(18):
        x = 646 + i * 24
        h = 12 + (i % 6) * 7
        color = (C["gold"], C["purple"], C["green"])[i % 3]
        pulse_bars.append(
            f'<rect x="{x}" y="{318-h}" width="12" height="{h}" rx="2" fill="{color}" opacity=".35">'
            f'<animate attributeName="height" values="{h};{h+18};{h}" dur="{2.7+(i%5)*.35}s" begin="-{i*.11:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{318-h};{300-h};{318-h}" dur="{2.7+(i%5)*.35}s" begin="-{i*.11:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )

    body = f"""
<text x="42" y="45" fill="{C['muted']}" font-size="11" font-family="Segoe UI" letter-spacing="2.5">RYF / LIVE PUBLIC SYSTEM</text>
<text x="42" y="100" fill="{C['text']}" font-size="46" font-weight="800" font-family="Segoe UI">CONTROL FIELD</text>
<rect x="42" y="119" width="452" height="3" rx="1.5" fill="url(#accent)"/>
<text x="42" y="158" fill="{C['sub']}" font-size="16.5" font-family="Segoe UI">AI-native product builder · public signals only</text>
{''.join(status_svg)}
<text x="42" y="306" fill="{C['muted']}" font-size="10.5" font-family="Segoe UI" letter-spacing="1.4">TOP PUBLIC REPO / {esc(top)}</text>
<text x="42" y="328" fill="{C['muted']}" font-size="9.5" font-family="Segoe UI">REFRESHED {NOW.strftime('%Y-%m-%d %H:%M UTC')}</text>

<g>
  <circle cx="952" cy="173" r="111" fill="url(#radarGlow)"/>
  <circle cx="952" cy="173" r="103" fill="#09130f" stroke="{C['grid']}"/>
  <circle cx="952" cy="173" r="82" fill="none" stroke="{C['grid']}"/>
  <circle cx="952" cy="173" r="60" fill="none" stroke="{C['grid']}"/>
  <circle cx="952" cy="173" r="37" fill="none" stroke="{C['grid']}"/>
  <path d="M952 70V276M849 173H1055M879 100L1025 246M1025 100L879 246" stroke="{C['grid']}" opacity=".85"/>
  <g>
    <path d="M952 173L952 70A103 103 0 0 1 1025 100Z" fill="{C['green']}" opacity=".17"/>
    <line x1="952" y1="173" x2="952" y2="70" stroke="{C['green']}" stroke-width="2.2"/>
    <animateTransform attributeName="transform" type="rotate" values="0 952 173;360 952 173" dur="3.4s" repeatCount="indefinite"/>
  </g>
  <circle cx="952" cy="173" r="5" fill="{C['text']}"/>
  <circle cx="913" cy="137" r="4" fill="{C['gold']}">
    <animate attributeName="r" values="3;7;3" dur="2.4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".35;1;.35" dur="2.4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="1009" cy="205" r="4" fill="{C['purple']}">
    <animate attributeName="r" values="3;6;3" dur="3.1s" begin="-.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".3;1;.3" dur="3.1s" begin="-.8s" repeatCount="indefinite"/>
  </circle>
  <circle cx="982" cy="114" r="4" fill="{C['green']}">
    <animate attributeName="r" values="3;7;3" dur="2.8s" begin="-1.2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".3;1;.3" dur="2.8s" begin="-1.2s" repeatCount="indefinite"/>
  </circle>
</g>

<g>{''.join(pulse_bars)}</g>
<rect x="638" y="278" width="58" height="54" fill="url(#accent)" opacity=".12">
  <animate attributeName="x" values="638;1038;638" dur="4.8s" repeatCount="indefinite"/>
</rect>
"""
    return shell(body, 1120, 360, "RYF live control field")

def activity_field(profile):
    events = profile["events"][:24]
    event_colors = {
        "PushEvent": C["gold"],
        "PullRequestEvent": C["purple"],
        "IssuesEvent": C["green"],
        "CreateEvent": C["blue"],
        "IssueCommentEvent": "#f0883e",
    }

    # Dense geometric field. Public events become the brighter anchors.
    dots = []
    rows = 9
    cols = 19
    for r in range(rows):
        for c in range(cols):
            x = 64 + c * 55 + r * 6
            base = 128 + r * 26 + math.sin(c * .72 + r * .53) * 18
            amp = 7 + ((c + r) % 5) * 2
            y1 = base
            y2 = base - amp
            y3 = base + amp * .55
            color = C["gold"] if c < 6 else (C["purple"] if c < 13 else C["green"])
            radius = 1.15 + r * .16 + (c % 3) * .12
            dur = 2.8 + ((r * 3 + c) % 7) * .37
            begin = -((c * .11 + r * .19) % 2.7)
            dots.append(
                f'<circle cx="{x:.1f}" cy="{y1:.1f}" r="{radius:.2f}" fill="{color}" opacity=".30">'
                f'<animate attributeName="cy" values="{y1:.1f};{y2:.1f};{y3:.1f};{y1:.1f}" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values=".18;.72;.18" dur="{dur+.7:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                f'</circle>'
            )

    grid_lines = []
    for r in range(rows):
        pts = []
        for c in range(cols):
            x = 64 + c * 55 + r * 6
            y = 128 + r * 26 + math.sin(c * .72 + r * .53) * 18
            pts.append(f"{x:.1f},{y:.1f}")
        grid_lines.append(
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{C["grid"]}" stroke-width=".8" opacity=".35"/>'
        )

    anchors = []
    for i, event in enumerate(events):
        col = i % 12
        row = (i * 5) % 7
        x = 180 + col * 72 + (row % 3) * 8
        y = 118 + row * 31 + math.sin(i * .83) * 12
        color = event_colors.get(event["type"], C["blue"])
        anchors.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{color}" filter="url(#glow)">'
            f'<animate attributeName="r" values="2.8;6.8;2.8" dur="{2.1+(i%5)*.33:.2f}s" begin="-{i*.09:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".4;1;.4" dur="{2.1+(i%5)*.33:.2f}s" begin="-{i*.09:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    body = f"""
<text x="34" y="42" fill="{C['muted']}" font-size="11.5" font-family="Segoe UI" letter-spacing="2.4">PUBLIC ACTIVITY FIELD / RECENT EVENTS</text>
<text x="34" y="80" fill="{C['text']}" font-size="28" font-weight="800" font-family="Segoe UI">GENERATIVE SIGNAL TERRAIN</text>
<text x="34" y="106" fill="{C['muted']}" font-size="12.5" font-family="Segoe UI">Public GitHub events are mapped into a moving geometric field. Private work is not queried.</text>

<g opacity=".75">{''.join(grid_lines)}</g>
<g>{''.join(dots)}</g>
<g>{''.join(anchors)}</g>

<rect x="-160" y="112" width="160" height="258" fill="url(#accent)" opacity=".08">
  <animate attributeName="x" values="-160;1180" dur="4.6s" repeatCount="indefinite"/>
</rect>
<line x1="40" y1="372" x2="1080" y2="372" stroke="{C['grid']}" opacity=".55"/>
<circle cx="52" cy="372" r="3.2" fill="{C['green']}">
  <animate attributeName="cx" values="52;1068;52" dur="6.2s" repeatCount="indefinite"/>
  <animate attributeName="fill" values="{C['gold']};{C['purple']};{C['green']};{C['gold']}" dur="6.2s" repeatCount="indefinite"/>
</circle>
"""
    return shell(body, 1120, 410, "RYF generative public activity field")

def terminal(profile):
    repos = profile["repos"][:4]
    events = profile["events"][:5]

    repo_lines = []
    for i, repo in enumerate(repos):
        y = 115 + i * 27
        repo_lines.append(
            f'<text x="608" y="{y}" fill="{C["muted"]}" font-size="11" font-family="monospace">{i+1:02d}</text>'
            f'<text x="642" y="{y}" fill="{C["sub"]}" font-size="12.5" font-family="monospace">{esc(repo["name"][:34])}</text>'
        )

    event_names = {
        "PushEvent": "push",
        "PullRequestEvent": "pull-request",
        "IssuesEvent": "issue",
        "CreateEvent": "create",
        "IssueCommentEvent": "comment",
    }
    event_lines = []
    for i, event in enumerate(events):
        y = 115 + i * 27
        color = (C["gold"], C["purple"], C["green"], C["blue"], "#f0883e")[i % 5]
        event_lines.append(
            f'<g opacity=".72"><animate attributeName="opacity" values=".38;1;.38" dur="{2.4+i*.35:.2f}s" begin="-{i*.3:.2f}s" repeatCount="indefinite"/>'
            f'<text x="44" y="{y}" fill="{color}" font-size="11" font-family="monospace">&gt;</text>'
            f'<text x="65" y="{y}" fill="{C["sub"]}" font-size="12.5" font-family="monospace">{esc(event_names.get(event["type"], "event"))}</text>'
            f'<text x="198" y="{y}" fill="{C["muted"]}" font-size="12.5" font-family="monospace">{esc(event["repo"][:28])}</text></g>'
        )

    body = f"""
<circle cx="26" cy="26" r="5" fill="#ff5f56"/>
<circle cx="44" cy="26" r="5" fill="#ffbd2e"/>
<circle cx="62" cy="26" r="5" fill="#27c93f"/>
<text x="90" y="31" fill="{C['muted']}" font-size="10.5" font-family="monospace">ryf@github / public-console</text>

<text x="42" y="72" fill="{C['green']}" font-size="13" font-family="monospace">ryf@github:~$ public-stream --follow</text>
<text x="42" y="94" fill="{C['muted']}" font-size="10" font-family="Segoe UI" letter-spacing="1.6">RECENT EVENTS</text>
{''.join(event_lines)}

<line x1="560" y1="78" x2="560" y2="236" stroke="{C['grid']}"/>
<text x="608" y="94" fill="{C['muted']}" font-size="10" font-family="Segoe UI" letter-spacing="1.6">RECENTLY PUSHED PUBLIC REPOS</text>
{''.join(repo_lines)}

<rect x="42" y="243" width="8" height="15" fill="{C['green']}">
  <animate attributeName="opacity" values="1;0;1" dur=".9s" repeatCount="indefinite"/>
</rect>
<text x="608" y="246" fill="{C['muted']}" font-size="10.5" font-family="monospace">production/private: sealed</text>
"""
    return shell(body, 1120, 275, "RYF public system console")

def signal(profile):
    state_path = DATA / "signal.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {
        "position": "C3",
        "actor": "system",
        "issue": 0,
    }
    pos = state.get("position", "C3")
    file_index = "ABCDEFGH".find(pos[0])
    rank_index = "87654321".find(pos[1])

    x0, y0, cell = 54, 50, 34
    cells = []
    for r in range(8):
        for c in range(8):
            fill = "#151a21" if (r + c) % 2 == 0 else "#0f1319"
            cells.append(
                f'<rect x="{x0+c*cell}" y="{y0+r*cell}" width="{cell}" height="{cell}" fill="{fill}"/>'
            )
    px = x0 + file_index * cell + cell / 2
    py = y0 + rank_index * cell + cell / 2

    allowed = [("A1", C["gold"]), ("C3", C["purple"]), ("F5", C["green"]), ("H7", C["blue"])]
    ports = []
    for i, (name, color) in enumerate(allowed):
        x = 508 + i * 132
        ports.append(
            f'<rect x="{x}" y="224" width="106" height="46" rx="10" fill="#0d1117" stroke="{color}" opacity=".92"/>'
            f'<text x="{x+53}" y="253" text-anchor="middle" fill="{color}" font-size="18" font-weight="800" font-family="Segoe UI">{name}</text>'
        )

    body = f"""
<text x="38" y="35" fill="{C['muted']}" font-size="11" font-family="Segoe UI" letter-spacing="2.2">ISSUE-DRIVEN INTERACTION / VISITOR SIGNAL</text>
<g>{''.join(cells)}</g>
<circle cx="{px:.1f}" cy="{py:.1f}" r="9" fill="{C['green']}" opacity=".22">
  <animate attributeName="r" values="9;26;9" dur="1.9s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".25;0;.25" dur="1.9s" repeatCount="indefinite"/>
</circle>
<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="{C['green']}"/>

<text x="506" y="72" fill="{C['muted']}" font-size="10.5" font-family="Segoe UI" letter-spacing="1.5">CURRENT POSITION</text>
<text x="506" y="128" fill="{C['text']}" font-size="54" font-weight="800" font-family="Segoe UI">{esc(pos)}</text>
<text x="506" y="162" fill="{C['sub']}" font-size="14" font-family="Segoe UI">last moved by @{esc(state.get('actor', 'system'))}</text>
<text x="506" y="190" fill="{C['muted']}" font-size="12" font-family="Segoe UI">Open a bounded public Issue to move the signal.</text>
<text x="506" y="208" fill="{C['muted']}" font-size="11" font-family="Segoe UI">The Action validates one of four allowed coordinates, updates state, then closes the Issue.</text>

{''.join(ports)}

<path d="M506 292H1032" stroke="{C['grid']}"/>
<circle cx="518" cy="292" r="3" fill="{C['green']}">
  <animate attributeName="cx" values="518;1020;518" dur="4.4s" repeatCount="indefinite"/>
</circle>
"""
    return shell(body, 1120, 340, "RYF issue-driven visitor signal")

def main():
    profile = load_public()

    outputs = {
        "hud.svg": hud(profile),
        "field.svg": activity_field(profile),
        "terminal.svg": terminal(profile),
        "signal.svg": signal(profile),
    }
    for name, svg in outputs.items():
        (OUT / name).write_text(svg, encoding="utf-8")

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
