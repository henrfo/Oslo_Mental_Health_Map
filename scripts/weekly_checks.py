"""
Weekly checks, run by .github/workflows/weekly_checks.yml.

  python scripts/weekly_checks.py links
      Opens each entry's website and writes _data/health.yml
      ({slug: {status: ok|broken, checked: date}}). A broken link fades the
      row and adds a "Brutt lenke" tag on the site. Only 404/410, server
      errors and unreachable hosts count as broken; 401/403/429 usually mean
      the site blocks bots, so those count as ok.

  python scripts/weekly_checks.py sources [--issues]
      For entries with `kilde` (the page their nar/sesong info comes from),
      fetches the page, extracts its text and compares it with last week's
      copy in _snapshots/. When it changed, it opens a GitHub issue with the
      diff (with --issues, via the gh CLI) so a person can update the entry.
      It never edits the entry data: scraped pages change format, and a wrong
      time in a clinical tool is worse than an outdated one.

The slug matches Jekyll's `slugify`, which index.html uses to look up health.yml.
"""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / '_data' / 'entries'
HEALTH = ROOT / '_data' / 'health.yml'
SNAPSHOTS = ROOT / '_snapshots' / 'sources'
USER_AGENT = 'OsloMentalHealthMap-weekly-check (+https://github.com/henrfo/Oslo_Mental_Health_Map)'
NOT_BROKEN = {401, 403, 429}   # usually bot blocking, not a dead page
MAX_DIFF_LINES = 80


def slugify(name: str) -> str:
    """Same result as Jekyll's default slugify."""
    return re.sub(r'[\W_]+', '-', name.lower()).strip('-')


def entries() -> list[dict]:
    out = []
    for f in sorted(ENTRIES.glob('*.yml')):
        out += yaml.safe_load(f.read_text(encoding='utf-8')) or []
    return out


def fetch(url: str) -> tuple[int | None, str]:
    """Return (HTTP status or None if unreachable, body text)."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except (urllib.error.URLError, TimeoutError, OSError):
        return None, ''


# ── links ──

def check_links() -> None:
    health = {}
    for e in entries():
        if not e.get('website'):
            continue
        status, _ = fetch(e['website'])
        broken = status is None or (status >= 400 and status not in NOT_BROKEN)
        health[slugify(e['name'])] = {'status': 'broken' if broken else 'ok', 'checked': date.today()}
        print(f"{'BROKEN' if broken else 'ok':6} {status} {e['name']}")
    HEALTH.write_text(
        '# Written by scripts/weekly_checks.py links — do not edit by hand.\n'
        + yaml.safe_dump(health, allow_unicode=True, sort_keys=True),
        encoding='utf-8',
    )


# ── sources ──

class TextExtractor(HTMLParser):
    """Visible text, one block per line, without scripts and styles."""
    BLOCKS = {'p', 'div', 'li', 'tr', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'article', 'td', 'th'}
    SKIP = {'script', 'style', 'noscript', 'svg'}

    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCKS:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag in self.BLOCKS:
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def text(self) -> str:
        lines = (re.sub(r'\s+', ' ', line).strip() for line in ''.join(self.parts).split('\n'))
        return '\n'.join(line for line in lines if line) + '\n'


def page_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    return parser.text()


def open_issue(title: str, body: str) -> None:
    """Open an issue unless an open one with the same title exists."""
    found = subprocess.run(
        ['gh', 'issue', 'list', '--state', 'open', '--search', f'"{title}" in:title', '--json', 'title'],
        capture_output=True, text=True, check=True,
    )
    if any(i['title'] == title for i in json.loads(found.stdout or '[]')):
        print(f'  issue already open: {title}')
        return
    subprocess.run(['gh', 'issue', 'create', '--title', title, '--body', body, '--label', 'kilde-endring'], check=True)
    print(f'  opened issue: {title}')


def check_sources(create_issues: bool) -> None:
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    for e in entries():
        url = e.get('kilde')
        if not url:
            continue
        name, slug = e['name'], slugify(e['name'])
        snapshot = SNAPSHOTS / f'{slug}.txt'
        status, html = fetch(url)

        if status is None or status >= 400:
            print(f'UNREACHABLE {status} {name}')
            if create_issues:
                open_issue(f'Kilde utilgjengelig: {name}',
                           f'The source page for **{name}** could not be fetched (status: {status}).\n\n'
                           f'Kilde: {url}\n\nCheck whether it moved and update `kilde` in the entry.')
            continue

        new = page_text(html)
        if not snapshot.exists():
            snapshot.write_text(new, encoding='utf-8')
            print(f'baseline   {name}')
            continue
        old = snapshot.read_text(encoding='utf-8')
        if old == new:
            print(f'unchanged  {name}')
            continue

        diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), 'forrige uke', 'denne uken', lineterm='', n=1))
        shown = '\n'.join(diff[:MAX_DIFF_LINES]) + ('\n…' if len(diff) > MAX_DIFF_LINES else '')
        print(f'CHANGED    {name}')
        if create_issues:
            when = e.get('nar') or {}
            season = e.get('sesong') or {}
            open_issue(
                f'Kilde endret: {name}',
                f'The source page for **{name}** changed since last week. Check whether the times, '
                f'season or group changed, and update the entry by hand if so.\n\n'
                f'Kilde: {url}\n\n'
                f'Current entry: `nar` = {json.dumps(when, ensure_ascii=False, default=str)}, '
                f'`sesong` = {json.dumps(season, ensure_ascii=False, default=str)}\n\n'
                f'```diff\n{shown}\n```\n\n'
                f'_Opened by the weekly source check. It never edits the data; a person approves every change._',
            )
        snapshot.write_text(new, encoding='utf-8')


if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else ''
    if command == 'links':
        check_links()
    elif command == 'sources':
        check_sources('--issues' in sys.argv)
    else:
        sys.exit(__doc__)
