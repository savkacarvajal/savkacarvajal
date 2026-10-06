#!/usr/bin/env python3
"""
Genera dist/streak.svg (racha de contribuciones) con la paleta negro/rojo del perfil.

Lo corre la Action .github/workflows/snake.yml junto a la serpiente, así el README no
depende de servicios externos que se caen por límites de la API de GitHub.

    GITHUB_TOKEN=... GITHUB_USER=savkacarvajal python scripts/generate_streak.py [salida.svg]
"""
import datetime as dt
import json
import os
import sys
import urllib.request

USER = os.environ.get("GITHUB_USER", "savkacarvajal")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "dist/streak.svg"


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "streak-svg"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]


created = gql("query($u:String!){user(login:$u){createdAt}}", u=USER)["user"]["createdAt"]
first_year = int(created[:4])
today = dt.date.today()

days = {}
for year in range(first_year, today.year + 1):
    cal = gql(
        """query($u:String!,$from:DateTime!,$to:DateTime!){user(login:$u){
        contributionsCollection(from:$from,to:$to){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}""",
        u=USER, **{"from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"},
    )["user"]["contributionsCollection"]["contributionCalendar"]
    for w in cal["weeks"]:
        for d in w["contributionDays"]:
            days[d["date"]] = d["contributionCount"]

dates = sorted(d for d in days if d <= today.isoformat())
total = sum(days[d] for d in dates)

# racha más larga y racha actual (si hoy aún no tiene contribuciones, cuenta desde ayer)
longest = run = 0
for d in dates:
    run = run + 1 if days[d] else 0
    longest = max(longest, run)
cur_end = len(dates) - 1
if cur_end >= 0 and not days[dates[cur_end]]:
    cur_end -= 1
current = 0
while cur_end >= 0 and days[dates[cur_end]]:
    current += 1
    cur_end -= 1

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
cols = [
    (total, "Contribuciones totales", f"{first_year} – {today.year}"),
    (current, "Racha actual", "días seguidos"),
    (longest, "Racha más larga", "días seguidos"),
]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="495" height="130" viewBox="0 0 495 130" role="img" aria-label="Racha de contribuciones">',
         '<rect width="495" height="130" rx="8" fill="#0D0D0D"/>']
for i, (num, label, sub) in enumerate(cols):
    cx = 82 + i * 165
    if i == 1:
        parts.append(f'<circle cx="{cx}" cy="52" r="34" fill="none" stroke="#C1121F" stroke-width="5"/>')
        num_fill, label_fill = "#E6E6E6", "#C1121F"
    else:
        num_fill, label_fill = "#E6E6E6", "#9A9A9A"
    parts.append(f'<text x="{cx}" y="60" text-anchor="middle" font-family="{FONT}" font-size="24" font-weight="700" fill="{num_fill}">{num}</text>')
    parts.append(f'<text x="{cx}" y="108" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{label_fill}">{label}</text>')
    parts.append(f'<text x="{cx}" y="124" text-anchor="middle" font-family="{FONT}" font-size="10" fill="#9A9A9A">{sub}</text>')
for x in (165, 330):
    parts.append(f'<line x1="{x}" y1="22" x2="{x}" y2="108" stroke="#2a2a2a"/>')
parts.append("</svg>")

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(parts))
print(f"total={total} actual={current} mas_larga={longest} -> {OUT}")
