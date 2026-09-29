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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="482" viewBox="0 0 1120 482" role="img">
<title>RYF chess strategy hero</title>
<defs>
  <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#d8b86a" stop-opacity="0"/>
    <stop offset=".5" stop-color="#f2d58b" stop-opacity=".22"/>
    <stop offset="1" stop-color="#d8b86a" stop-opacity="0"/>
  </linearGradient>
  <filter id="blur" x="-300%" y="-300%" width="600%" height="600%">
    <feGaussianBlur stdDeviation="7"/>
  </filter>
</defs>
<rect width="1120" height="482" rx="28" fill="#07090d"/>
<image href="../chess-hero.jpg" x="0" y="0" width="1120" height="482" preserveAspectRatio="xMidYMid slice"/>
<rect x="1" y="1" width="1118" height="480" rx="27" fill="none" stroke="#2a2d31"/>

<!-- moving light over the king / board -->
<rect x="560" y="20" width="72" height="430" fill="url(#scan)" filter="url(#blur)" opacity=".75">
  <animate attributeName="x" values="560;1040;560" dur="7.4s" repeatCount="indefinite"/>
</rect>

<!-- orbit tracers -->
<g transform="rotate(8 825 245)">
  <ellipse cx="825" cy="245" rx="205" ry="62" fill="none" stroke="#d8b86a" stroke-width="1.4" opacity=".28"/>
  <circle cx="1030" cy="245" r="4.2" fill="#f2d58b" filter="url(#blur)"/>
  <animateTransform attributeName="transform" type="rotate" values="8 825 245;368 825 245" dur="18s" repeatCount="indefinite"/>
</g>
<g transform="rotate(48 825 245)">
  <ellipse cx="825" cy="245" rx="178" ry="80" fill="none" stroke="#9b87ff" stroke-width="1.2" opacity=".22"/>
  <circle cx="1003" cy="245" r="3.8" fill="#c4b5fd"/>
  <animateTransform attributeName="transform" type="rotate" values="48 825 245;-312 825 245" dur="24s" repeatCount="indefinite"/>
</g>
<g transform="rotate(82 825 245)">
  <ellipse cx="825" cy="245" rx="152" ry="97" fill="none" stroke="#48e59b" stroke-width="1.1" opacity=".18"/>
  <circle cx="977" cy="245" r="3.4" fill="#48e59b"/>
  <animateTransform attributeName="transform" type="rotate" values="82 825 245;442 825 245" dur="29s" repeatCount="indefinite"/>
</g>

<!-- tactical nodes -->
<g>
  <circle cx="760" cy="178" r="4" fill="#d8b86a">
    <animate attributeName="r" values="2.5;7;2.5" dur="2.7s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".35;1;.35" dur="2.7s" repeatCount="indefinite"/>
  </circle>
  <circle cx="905" cy="132" r="4" fill="#9b87ff">
    <animate attributeName="r" values="2.5;6.5;2.5" dur="3.1s" begin="-1s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".3;1;.3" dur="3.1s" begin="-1s" repeatCount="indefinite"/>
  </circle>
  <circle cx="988" cy="278" r="4" fill="#48e59b">
    <animate attributeName="r" values="2.5;7;2.5" dur="3.6s" begin="-1.7s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".3;1;.3" dur="3.6s" begin="-1.7s" repeatCount="indefinite"/>
  </circle>
</g>

<!-- board signal -->
<circle cx="620" cy="448" r="3.2" fill="#f2d58b">
  <animate attributeName="cx" values="620;1050;620" dur="6.2s" repeatCount="indefinite"/>
  <animate attributeName="fill" values="#f2d58b;#9b87ff;#48e59b;#f2d58b" dur="6.2s" repeatCount="indefinite"/>
</circle>
<text x="22" y="468" fill="#7d8590" font-size="9.5" font-family="monospace">animated profile system · refreshed {updated}</text>
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
