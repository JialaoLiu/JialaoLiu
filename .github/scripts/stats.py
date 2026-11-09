"""Writes assets/stats.svg: total stars, commits, pull requests and issues for one GitHub user.
   python .github/scripts/stats.py <user>     (GITHUB_TOKEN in the environment is used when set)"""
import json
import os
import sys
import urllib.request
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else 'JialaoLiu'
OUT = Path(__file__).resolve().parents[2] / 'assets' / 'stats.svg'

BG, PANEL, LINE, FG, MUTED, ACC = '#FFFFFF', '#F4F6FA', '#E2E7EF', '#0F172A', '#5B6577', '#2563EB'
SANS = '-apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, sans-serif'
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'


def get(path):
    req = urllib.request.Request('https://api.github.com' + path, headers={'Accept': 'application/vnd.github+json',
                                                                          'User-Agent': USER + '-profile-stats'})
    if os.environ.get('GITHUB_TOKEN'):
        req.add_header('Authorization', 'Bearer ' + os.environ['GITHUB_TOKEN'])
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def stars():
    total, page = 0, 1
    while True:
        repos = get(f'/users/{USER}/repos?per_page=100&type=owner&page={page}')
        total += sum(r['stargazers_count'] for r in repos if not r['fork'])
        if len(repos) < 100:
            return total
        page += 1


def count(q):
    kind = 'commits' if q.startswith('author:') and 'type:' not in q else 'issues'
    return get(f'/search/{kind}?q={q}&per_page=1')['total_count']


def fmt(n):
    return f'{n / 1000:.1f}k' if n >= 10000 else f'{n:,}'


def svg(items):
    W, gap, x0, y0, H = 254, 18, 64, 64, 120
    b = [f'<text x="64" y="42" font-family="{MONO}" font-size="15" fill="{ACC}" letter-spacing="2">GITHUB STATS</text>']
    for i, (label, n) in enumerate(items):
        x = x0 + i * (W + gap)
        b.append(f'<rect x="{x}" y="{y0}" width="{W}" height="{H}" rx="16" fill="{PANEL}" stroke="{LINE}" stroke-width="1"/>')
        b.append(f'<text x="{x + 24}" y="{y0 + 62}" font-family="{SANS}" font-size="40" font-weight="700" fill="{FG}">{fmt(n)}</text>')
        b.append(f'<text x="{x + 24}" y="{y0 + 96}" font-family="{SANS}" font-size="18" fill="{MUTED}">{label}</text>')
    desc = ', '.join(f'{fmt(n)} {label.lower()}' for label, n in items)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{y0 + H + 24}" viewBox="0 0 1200 {y0 + H + 24}" '
            f'role="img" aria-labelledby="title desc">\n  <title id="title">GitHub stats</title>\n'
            f'  <desc id="desc">{desc}.</desc>\n  <rect width="1200" height="{y0 + H + 24}" rx="24" fill="{BG}"/>\n'
            + '\n'.join(b) + '\n</svg>\n')


items = [('Stars', stars()), ('Commits', count(f'author:{USER}')),
         ('Pull requests', count(f'author:{USER}+type:pr')), ('Issues', count(f'author:{USER}+type:issue'))]
OUT.write_text(svg(items), encoding='utf-8', newline='\n')
print('wrote', OUT, items)
