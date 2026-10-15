"""Offline guard for the PR62 asset-path regression, not a full asset audit.

Scope: tracked root HTML (excluding backup names), root index.php, and one-level
slug/index.html. Mirrors, tools, staging/upload directories and other PHP/ASP
sources are intentionally outside scope. No network requests or file changes.
"""
import argparse
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import subprocess
import sys
from urllib.parse import urlsplit

TARGETS = {'js/main.js', 'js/booking.js', 'css/styles.css'}
EXCLUDED_DIRS = {'colddirect-public-html', 'tools', 'docs', 'agent', 'scripts',
                 'plesk-upload', 'plesk-hero-upload', 'node_modules'}


def in_scope(name):
    path = PurePosixPath(name)
    if any(part.startswith(('.', '_')) or 'backup' in part.lower()
           for part in path.parts):
        return False
    if path.parts[0] in EXCLUDED_DIRS:
        return False
    return (len(path.parts) == 1 and (path.suffix == '.html' or name == 'index.php')
            or len(path.parts) == 2 and path.name == 'index.html')


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            value = attrs.get('src')
            allowed = {'js/main.js', 'js/booking.js'}
        elif tag == 'link' and 'stylesheet' in (attrs.get('rel') or '').lower().split():
            value = attrs.get('href')
            allowed = {'css/styles.css'}
        else:
            return
        if not value:
            return
        value = value.strip()
        try:
            parsed = urlsplit(value)
        except ValueError:
            return
        if parsed.scheme or parsed.netloc or parsed.path.startswith('/'):
            return
        path = parsed.path
        while path.startswith('./') or path.startswith('../'):
            path = path[2:] if path.startswith('./') else path[3:]
        if path in allowed:
            self.errors.append((self.getpos()[0], path))


def inspect(source):
    parser = AssetParser()
    parser.feed(source)
    return parser.errors


def validate(root):
    names = subprocess.check_output(
        ['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    failures = []
    pages = [name for name in names if name and in_scope(name)]
    if not pages:
        failures.append('No tracked pages found within documented scope')
    for name in sorted(pages):
        path = root / name
        if not path.is_file():
            failures.append(f'{name}: tracked page missing')
            continue
        for line, asset in inspect(path.read_text(encoding='utf-8')):
            failures.append(f'{name}:{line}: relative asset reference; use /{asset}')
    for asset in sorted(TARGETS):
        if not (root / asset).is_file():
            failures.append(f'{asset}: required root asset missing')
    return len(pages), failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        count, failures = validate(args.root)
    except (OSError, UnicodeError, subprocess.CalledProcessError) as exc:
        print(f'FAIL: unable to validate source tree ({type(exc).__name__})', file=sys.stderr)
        return 1
    for failure in failures:
        print(f'FAIL {failure}', file=sys.stderr)
    if failures:
        return 1
    print(f'PASS asset-path guard: {count} tracked pages; 3 root assets exist (offline)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
