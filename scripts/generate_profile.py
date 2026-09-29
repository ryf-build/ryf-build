#!/usr/bin/env python3
import datetime as dt, html, json, math, os, pathlib, urllib.request
R=pathlib.Path(__file__).resolve().parents[1]; O=R/'assets'/'generated'; D=R/'data'; O.mkdir(parents=True,exist_ok=True); D.mkdir(exist_ok=True)
U=os.getenv('GITHUB_REPOSITORY_OWNER','ryf-build'); T=os.getenv('GITHUB_TOKEN',''); N=dt.datetime.now(dt.timezone.utc)
C={'g':'#e3bd62','p':'#a78bfa','n':'#63e6a1','b':'#090b0f','q':'#0d1117','x':'#21262d','t':'#f0f6fc','s':'#c9d1d9','m':'#7d8590','d':'#27303a'}
def E(x): return html.escape(str(x),quote=True)
def req(url,data=None):
 h={'User-Agent':'ryf-profile','Accept':'application/vnd.github+json'}
 if T:h['Authorization']='Bearer '+T
 if data is not None:h['Content-Type']='application/json'
 q=urllib.request.Request(url,data=data,headers=h,method='POST' if data else 'GET')
 return json.loads(urllib.request.urlopen(q,timeout=20).read())
def load():
 user=req(f'https://api.github.com/users/{U}'); repos=req(f'https://api.github.com/users/{U}/repos?per_page=100&sort=pushed'); events=req(f'https://api.github.com/users/{U}/events/public?per_page=30')
 days=[]; total=0
 if T:
  a=(N-dt.timedelta(days=370)).isoformat().replace('+00:00','Z'); z=N.isoformat().replace('+00:00','Z')
  query='query($u:String!,$a:DateTime!,$z:DateTime!){user(login:$u){contributionsCollection(from:$a,to:$z){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
  try:
   g=req('https://api.github.com/graphql',json.dumps({'query':query,'variables':{'u':U,'a':a,'z':z}}).encode()); cal=g['data']['user']['contributionsCollection']['contributionCalendar']; total=cal['totalContributions']; days=[{'date':d['date'],'count':d['contributionCount']} for w in cal['weeks'] for d in w['contributionDays']]
  except Exception as ex: print('contrib fallback',ex)
 if not days:
  by={}
  for e0 in events:
   k=e0.get('created_at','')[:10]
   if k:by[k]=by.get(k,0)+1
  st=N.date()-dt.timedelta(days=370); days=[{'date':(st+dt.timedelta(days=i)).isoformat(),'count':by.get((st+dt.timedelta(days=i)).isoformat(),0)} for i in range(371)]; total=sum(d['count'] for d in days)
 return {'user':user,'repos':[r for r in repos if not r.get('fork')],'events':events,'days':days[-371:],'total':total}
def sh(body,w,h,title):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{E(title)}</title><defs><linearGradient id="a"><stop stop-color="{C['g']}"/><stop offset=".52" stop-color="{C['p']}"/><stop offset="1" stop-color="{C['n']}"/></linearGradient><filter id="z" x="-300%" y="-300%" width="600%" height="600%"><feGaussianBlur stdDeviation="4"/></filter></defs><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="24" fill="{C['b']}" stroke="{C['x']}"/>{body}</svg>'''
def hud(P):
 u=P['user']; repos=P['repos']; ev=P['events']; top=repos[0]['name'] if repos else 'ryf-build'; total=P['total']; dots=''.join(f'<circle cx="{915+i*25}" cy="177" r="{4-i}" fill="{[C["g"],C["p"],C["n"]][i]}"><animateTransform attributeName="transform" type="rotate" values="0 952 177;360 952 177" dur="{7-i*1.2}s" begin="-{i}s" repeatCount="indefinite"/></circle>' for i in range(3))
 bars=''.join(f'<rect x="{650+i*28}" y="286" width="16" height="{10+(i%5)*5}" rx="2" fill="{[C["g"],C["p"],C["n"]][i%3]}" opacity=".{2+i%5}"/>' for i in range(15))
 return sh(f'''<text x="42" y="48" fill="{C['m']}" font-size="12" font-family="Segoe UI" letter-spacing="2.4">LIVE SYSTEM / PUBLIC GITHUB TELEMETRY</text><text x="42" y="104" fill="{C['t']}" font-size="47" font-family="Segoe UI" font-weight="800">RYF CONTROL FIELD</text><rect x="42" y="125" width="458" height="3" fill="url(#a)"/><text x="42" y="164" fill="{C['s']}" font-size="17" font-family="Segoe UI">AI-native product builder · public systems only</text><g font-family="Segoe UI"><text x="42" y="205" fill="{C['m']}" font-size="11">SYSTEM STATE</text><text x="42" y="243" fill="{C['n']}" font-size="24" font-weight="700">LIVE</text><text x="195" y="205" fill="{C['m']}" font-size="11">PUBLIC REPOS</text><text x="195" y="243" fill="{C['t']}" font-size="30" font-weight="700">{u.get('public_repos',0)}</text><text x="330" y="205" fill="{C['m']}" font-size="11">FOLLOWERS</text><text x="330" y="243" fill="{C['t']}" font-size="30" font-weight="700">{u.get('followers',0)}</text><text x="450" y="205" fill="{C['m']}" font-size="11">EVENTS / 30</text><text x="450" y="243" fill="{C['t']}" font-size="30" font-weight="700">{len(ev)}</text></g><g><circle cx="952" cy="177" r="103" fill="#0b1712" stroke="{C['d']}"/><circle cx="952" cy="177" r="88" fill="none" stroke="{C['d']}"/><circle cx="952" cy="177" r="62" fill="none" stroke="{C['d']}"/><circle cx="952" cy="177" r="39" fill="none" stroke="{C['d']}"/><path d="M952 74V280M849 177H1055M879 104L1025 250M1025 104L879 250" stroke="{C['d']}"/><g><path d="M952 177L952 76A101 101 0 0 1 1023 105Z" fill="{C['n']}" opacity=".16"/><line x1="952" y1="177" x2="952" y2="76" stroke="{C['n']}" stroke-width="2"/><animateTransform attributeName="transform" type="rotate" values="0 952 177;360 952 177" dur="4.3s" repeatCount="indefinite"/></g>{dots}<circle cx="952" cy="177" r="6" fill="{C['t']}"/></g>{bars}<rect x="650" y="274" width="34" height="58" fill="url(#a)" opacity=".2"><animate attributeName="x" values="650;1060;650" dur="5.2s" repeatCount="indefinite"/></rect><text x="42" y="328" fill="{C['m']}" font-size="11" font-family="Segoe UI">TOP PUBLIC REPO / {E(top)}</text><text x="42" y="348" fill="{C['m']}" font-size="10" font-family="Segoe UI">GENERATED {N.strftime('%Y-%m-%d %H:%M UTC')}</text>''',1120,370,'RYF live HUD')
def skyline(P):
 ds=P['days']; weeks=[ds[i:i+7] for i in range(0,len(ds),7)][-53:]; vs=[sum(d['count'] for d in w) for w in weeks]; mx=max(vs or [1]) or 1; bars=[]
 for i,v in enumerate(vs):
  h=5+190*math.sqrt(v/mx) if v else 4; x=38+i*20; y=302-h; col=C['g'] if i<18 else C['p'] if i<36 else C['n']; bars.append(f'<rect x="{x}" y="{y:.1f}" width="13" height="{h:.1f}" rx="2" fill="{col}" opacity=".72"/><polygon points="{x},{y:.1f} {x+6},{y-6:.1f} {x+19},{y-6:.1f} {x+13},{y:.1f}" fill="{col}"/><polygon points="{x+13},{y:.1f} {x+19},{y-6:.1f} {x+19},296 {x+13},302" fill="{col}" opacity=".38"/>')
 return sh(f'''<text x="30" y="40" fill="{C['m']}" font-size="12" font-family="Segoe UI" letter-spacing="2">PUBLIC ACTIVITY TERRAIN / 53 WEEKS</text><text x="30" y="78" fill="{C['t']}" font-size="28" font-family="Segoe UI" font-weight="800">PUBLIC SIGNAL · PRIVATE WORK SEALED</text><path d="M30 302H1090M30 252H1090M30 202H1090M30 152H1090" stroke="{C['d']}" opacity=".5"/>{''.join(bars)}<rect x="-150" y="100" width="150" height="210" fill="url(#a)" opacity=".18"><animate attributeName="x" values="-150;1140" dur="6.4s" repeatCount="indefinite"/></rect><text x="30" y="332" fill="{C['m']}" font-size="10" font-family="Segoe UI">OLDER</text><text x="1040" y="332" fill="{C['m']}" font-size="10" font-family="Segoe UI">NOW</text>''',1120,350,'Contribution terrain')
def heat(P):
 ds=P['days']; mx=max([d['count'] for d in ds]+[1]); cells=[]
 for i,d in enumerate(ds):
  x=28+(i//7)*11; y=78+(i%7)*11; n=d['count']; r=n/mx if mx else 0; col='#151b23' if n==0 else '#244d35' if r<.25 else '#2f7d4c' if r<.5 else '#46b96a' if r<.75 else C['n']; cells.append(f'<rect x="{x}" y="{y}" width="8" height="8" rx="1.5" fill="{col}"/>')
 active=sum(d['count']>0 for d in ds)
 return sh(f'''<text x="26" y="36" fill="{C['m']}" font-size="12" font-family="Segoe UI" letter-spacing="2">PUBLIC ACTIVITY HEATMAP</text><text x="26" y="60" fill="{C['t']}" font-size="16" font-family="Segoe UI" font-weight="700">{active} active days · peak {mx}/day</text>{''.join(cells)}<rect x="24" y="71" width="2" height="87" fill="{C['n']}"><animate attributeName="x" values="24;610;24" dur="5s" repeatCount="indefinite"/></rect>''',650,185,'Live heatmap')
def terminal(P):
 rs=P['repos'][:3]; lines=''.join(f'<text x="382" y="{108+i*25}" fill="{C["s"]}" font-size="12" font-family="monospace">{i+1}. {E(r["name"][:28])}</text>' for i,r in enumerate(rs)); u=P['user']
 return sh(f'''<circle cx="24" cy="25" r="5" fill="#ff5f56"/><circle cx="42" cy="25" r="5" fill="#ffbd2e"/><circle cx="60" cy="25" r="5" fill="#27c93f"/><text x="24" y="60" fill="{C['n']}" font-size="13" font-family="monospace">ryf@github:~$ profile --live</text><g font-family="monospace" font-size="12.5"><text x="24" y="94" fill="{C['p']}">login</text><text x="100" y="94" fill="{C['s']}">{E(u.get('login',U))}</text><text x="24" y="119" fill="{C['p']}">mode</text><text x="100" y="119" fill="{C['s']}">AI-native builder</text><text x="24" y="144" fill="{C['p']}">repos</text><text x="100" y="144" fill="{C['s']}">{u.get('public_repos',0)} public</text><text x="24" y="169" fill="{C['p']}">policy</text><text x="100" y="169" fill="{C['s']}">production stays private</text></g><path d="M352 76V177" stroke="{C['d']}"/><text x="382" y="84" fill="{C['m']}" font-size="10.5" font-family="Segoe UI" letter-spacing="1.8">RECENTLY PUSHED</text>{lines}<rect x="24" y="185" width="8" height="14" fill="{C['n']}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>''',650,214,'Terminal profile')
def activity(P):
 names={'PushEvent':'PUSH','PullRequestEvent':'PULL REQUEST','IssuesEvent':'ISSUE','CreateEvent':'CREATE','IssueCommentEvent':'COMMENT'}; out=[]
 for i,e0 in enumerate(P['events'][:6]):
  y=70+i*34; col=[C['g'],C['p'],C['n'],'#58a6ff'][i%4]; name=names.get(e0.get('type'),str(e0.get('type','EVENT')).replace('Event','').upper()); repo=e0.get('repo',{}).get('name','').split('/')[-1]; out.append(f'<circle cx="32" cy="{y-4}" r="4" fill="{col}"><animate attributeName="r" values="3;5;3" dur="{2.5+i*.2}s" repeatCount="indefinite"/></circle><text x="50" y="{y}" fill="{col}" font-size="10.5" font-family="Segoe UI" font-weight="700">{E(name)}</text><text x="170" y="{y}" fill="{C["s"]}" font-size="12.5" font-family="Segoe UI">{E(repo[:28])}</text>')
 return sh(f'<text x="24" y="34" fill="{C["m"]}" font-size="12" font-family="Segoe UI" letter-spacing="2">RECENT PUBLIC ACTIVITY</text><path d="M32 52V250" stroke="{C["d"]}"/>{"".join(out)}',440,280,'Recent activity')
def signal():
 p=D/'signal.json'; s=json.loads(p.read_text()) if p.exists() else {'position':'C3','actor':'system'}; pos=s.get('position','C3'); fi='ABCDEFGH'.find(pos[0]); ri='87654321'.find(pos[1]); x0,y0,cell=48,70,28; cells=''.join(f'<rect x="{x0+c*cell}" y="{y0+r*cell}" width="{cell}" height="{cell}" fill="{"#151a21" if (r+c)%2==0 else "#0f1319"}"/>' for r in range(8) for c in range(8)); px=x0+fi*cell+14; py=y0+ri*cell+14
 return sh(f'''<text x="28" y="36" fill="{C['m']}" font-size="12" font-family="Segoe UI" letter-spacing="2">VISITOR SIGNAL / ISSUE-DRIVEN</text>{cells}<circle cx="{px}" cy="{py}" r="8" fill="{C['n']}" opacity=".18"><animate attributeName="r" values="8;20;8" dur="2.2s" repeatCount="indefinite"/><animate attributeName="opacity" values=".18;0;.18" dur="2.2s" repeatCount="indefinite"/></circle><circle cx="{px}" cy="{py}" r="5.5" fill="{C['n']}"/><text x="310" y="98" fill="{C['m']}" font-size="11" font-family="Segoe UI">CURRENT POSITION</text><text x="310" y="140" fill="{C['t']}" font-size="38" font-family="Segoe UI" font-weight="800">{E(pos)}</text><text x="310" y="178" fill="{C['s']}" font-size="13" font-family="Segoe UI">last moved by @{E(s.get('actor','system'))}</text><text x="310" y="210" fill="{C['m']}" font-size="11" font-family="Segoe UI">Open a profile-move issue to change the signal.</text>''',650,320,'Visitor signal')
def main():
 P=load(); outputs={'hud.svg':hud(P),'skyline.svg':skyline(P),'heatmap.svg':heat(P),'terminal.svg':terminal(P),'activity.svg':activity(P),'signal.svg':signal()}
 for n,v in outputs.items():(O/n).write_text(v)
 (D/'snapshot.json').write_text(json.dumps(P,indent=2))
if __name__=='__main__': main()
