"""Static review of the Liebherr restore; actual server verification remains required."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
checks = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.h1s = []
        self.canonicals = []
        self.jsonld = []
        self.references = []
        self.mode = None
        self.buffer = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.references.extend(attrs[key] for key in ('href', 'src') if key in attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag in ('title', 'h1') or (tag == 'script' and attrs.get('type') == 'application/ld+json'):
            self.mode, self.buffer = tag, ''

    def handle_data(self, data):
        if self.mode:
            self.buffer += data

    def handle_endtag(self, tag):
        if self.mode == tag:
            if tag == 'title':
                self.title = self.buffer.strip()
            elif tag == 'h1':
                self.h1s.append(self.buffer.strip())
            elif tag == 'script':
                self.jsonld.append(json.loads(self.buffer))
            self.mode, self.buffer = None, ''


def directives(text):
    return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')]


def check(condition, description):
    assert condition, description
    checks.append(description)


before = (ROOT / 'before.html').read_text(encoding='utf-8-sig')
after = (ROOT / 'restored.html').read_text(encoding='utf-8-sig')
check(before.count('href="css/styles.css?v=navwrap3"') == 1, 'Exactly one existing relative stylesheet')
check(before.count('src="js/main.js"') == 1, 'Exactly one existing relative script')
check(after == before.replace('href="css/styles.css?v=navwrap3"', 'href="/css/styles.css?v=navwrap3"').replace('src="js/main.js"', 'src="/js/main.js"'), 'Only two asset references changed; all claims and content preserved')
original, restored = Page(), Page()
original.feed(before)
restored.feed(after)
check(original.title == restored.title == 'Emergency Same Day Liebherr Fridge Repair London | ColdDirect', 'Existing title preserved')
check(original.h1s == restored.h1s == ['Liebherr Fridge Repair in London'], 'Existing H1 preserved')
check(original.canonicals == restored.canonicals == ['https://www.colddirect.co.uk/liebherr-fridge-repair-london/'], 'Existing slash canonical preserved')
check(bool(original.jsonld) and original.jsonld == restored.jsonld, 'JSON-LD remains valid and unchanged')
check(all(ref.startswith(('/', '#')) or urlsplit(ref).scheme for ref in restored.references), 'All assets and links retain their meaning in directory')
index_rule = r'RewriteRule ^liebherr-fridge-repair-london/index\.html$ - [L]'
slash_rule = r'RewriteRule ^liebherr-fridge-repair-london/$ - [L]'
for prefix in ('root', 'mirror'):
    old = directives((ROOT / ('before-' + prefix + '.htaccess')).read_text(encoding='utf-8-sig'))
    new = directives((ROOT / (prefix + '.htaccess')).read_text(encoding='utf-8-sig'))
    check(new.count(index_rule) == new.count(slash_rule) == 1, prefix + ' exactly two explicit pass-through rules')
    check([line for line in new if line not in (index_rule, slash_rule)] == old, prefix + ' all existing directives and their order preserved')
    generic = next(i for i, line in enumerate(new) if line.startswith(r'RewriteRule ^(.*)\.html$'))
    https = next(i for i, line in enumerate(new) if 'https://%{HTTP_HOST}%{REQUEST_URI}' in line)
    pretty = next(i for i, line in enumerate(new) if line.startswith(r'RewriteRule ^(.+?)/?$'))
    alias = next(i for i, line in enumerate(new) if line.startswith(r'RewriteRule ^liebherr-fridge-repair-london/?$'))
    check(new.index(index_rule) < generic, prefix + ' index exemption before generic HTML redirect')
    check(https < new.index(slash_rule) < pretty and new.index(slash_rule) < alias, prefix + ' slash exemption after HTTPS and before generic/alias rules')
    for rule, exact in ((index_rule, 'liebherr-fridge-repair-london/index.html'), (slash_rule, 'liebherr-fridge-repair-london/')):
        pattern = rule.split()[1]
        check(re.fullmatch(pattern, exact) is not None, prefix + ' expected path matches ' + exact)
        check(all(re.fullmatch(pattern, path) is None for path in ('liebherr-fridge-repair-london', 'liebherr-fridge-repair-london.html', 'liebherr-repairs-london/', 'unrelated/index.html', 'services/', 'refrigeration-brands-repair-london/')), prefix + ' exact rule excludes other routes ' + exact)
print(json.dumps({'passed': len(checks), 'checks': checks, 'scope': 'Static content and configuration review; actual hosting, binary identity and deployed copies require separate verification.'}, indent=2))