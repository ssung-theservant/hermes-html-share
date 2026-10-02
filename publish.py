#!/usr/bin/env python3
"""Publish one explicitly selected HTML file to a GitHub Pages repository."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parent

def cmd(*args, capture=True):
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError(f"{' '.join(args[:3])} failed ({p.returncode}): {(p.stderr or p.stdout)[-1000:]}")
    return p.stdout.strip()

def main():
    ap = argparse.ArgumentParser(description='Publish a single local HTML document to GitHub Pages')
    ap.add_argument('html', type=Path, help='HTML file to publish; relative assets are NOT copied')
    ap.add_argument('--slug', required=True, help='URL segment, lowercase a-z, 0-9 and hyphen')
    ap.add_argument('--dry-run', action='store_true', help='stage and preview locally without git push')
    args = ap.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.slug):
        ap.error('slug must contain lowercase letters, digits, hyphens')
    source = args.html.expanduser().resolve(strict=True)
    if not source.is_file() or source.suffix.lower() not in ('.html', '.htm'):
        ap.error('select an existing .html or .htm file')
    data = source.read_bytes()
    if not data.strip():
        ap.error('HTML file is empty')
    target = ROOT / 'site' / args.slug / 'index.html'
    if target.exists() and target.read_bytes() != data:
        ap.error(f'{args.slug} already exists with different content; choose a new slug to avoid overwriting')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f'Staged {source} -> {target} ({len(data)} bytes)')
    if args.dry_run:
        print('DRY RUN: no GitHub changes or publishing')
        return
    if not shutil.which('gh'):
        raise RuntimeError('gh is not installed')
    cmd('gh', 'auth', 'status')
    repo = cmd('gh', 'repo', 'view', '--json', 'nameWithOwner,url', '--jq', '.nameWithOwner')
    visibility = cmd('gh', 'repo', 'view', '--json', 'visibility', '--jq', '.visibility')
    if visibility != 'PUBLIC':
        raise RuntimeError('Repository is not PUBLIC; GitHub Pages publishing is not configured')
    page = json.loads(cmd('gh', 'api', f'repos/{repo}/pages'))
    if not page.get('html_url'):
        raise RuntimeError('GitHub Pages is not enabled')
    # Show each untracked file individually so an unrelated file cannot hide under site/.
    dirty = cmd('git', 'status', '--porcelain', '--untracked-files=all')
    allowed = str(target.relative_to(ROOT))
    if dirty and any(line[3:] != allowed for line in dirty.splitlines()):
        raise RuntimeError('Unrelated git changes exist; review them before publishing')
    cmd('git', 'add', '--', allowed)
    if cmd('git', 'diff', '--cached', '--name-only'):
        cmd('git', 'commit', '-m', f'Publish HTML: {args.slug}')
        cmd('git', 'push', 'origin', 'main')
    url = page['html_url'].rstrip('/') + '/site/' + args.slug + '/'
    for _ in range(12):
        try:
            with urllib.request.urlopen(url, timeout=12) as response:
                if response.status == 200 and response.read() == data:
                    print('PUBLIC_URL_VERIFIED:', url)
                    return
        except Exception:
            pass
        time.sleep(10)
    raise RuntimeError(f'GitHub push completed, but published URL not verified yet: {url}')

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError) as exc:
        print('PUBLISH_FAILED:', exc, file=sys.stderr)
        sys.exit(1)
