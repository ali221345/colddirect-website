#!/usr/bin/env python3
"""Independent static validation of the narrow brands directory-index repair.

This validates staged fixtures and configuration intent, not an Apache/IIS server.
"""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

SLUG = 'refrigeration-brands-repair-london'
CANONICAL = 'https://www.colddirect.co.uk/' + SLUG + '/'
EXPECTED_RULE = r'RewriteRule ^refrigeration-brands-repair-london/index\.html$ - [L]'
TARGETS = {
    'appliances-repair-london': '/appliances-repair-london/',
    'catering-repair-london': '/catering-repair-london/',
    'chiller-repair-london': '/chiller-repair-london/',
    'bottle-cooler-repair': '/bottle-cooler-repair-london/',
    'display-fridge-repair': '/display-fridge-repair-london/',
}


def xml_identity(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or '').strip(), tuple(xml_identity(child) for child in node))


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.references = []
        self.title = ''
        self.h1s = []
        self.jsonld = []
        self.mode = None
        self.buffer = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('href', 'src'):
            if key in attrs:
                self.references.append(attrs[key])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag in ('title', 'h1') or (tag == 'script' and attrs.get('type') == 'application/ld+json'):
            self.mode, self.buffer = tag, ''

    def handle_data(self, data):
        if self.mode:
            self.buffer += data

    def handle_endtag(self, tag):
        if self.mode != tag:
            return
        if tag == 'title':
            self.title = self.buffer.strip()
        elif tag == 'h1':
            self.h1s.append(self.buffer.strip())
        elif tag == 'script':
            self.jsonld.append(json.loads(self.buffer))
        self.mode, self.buffer = None, ''


def directives(text):
    return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.directory
    passed = []
    mapping = {'source.html': 'refrigeration-brands-repair-london.html', 'root-index.html': 'refrigeration-brands-repair-london/index.html', 'mirror-index.html': 'colddirect-public-html/refrigeration-brands-repair-london/index.html', 'root.htaccess': '.htaccess', 'mirror.htaccess': 'colddirect-public-html/.htaccess', 'root-before.htaccess': 'tools/fixtures/public-404/before-root.htaccess', 'mirror-before.htaccess': 'tools/fixtures/public-404/before-mirror.htaccess', 'web-before.config': 'tools/fixtures/public-404/before-web.config', 'mirror-web-before.config': 'tools/fixtures/public-404/before-mirror-web.config', 'mirror-web.config': 'colddirect-public-html/web.config'}
    def fixture(name):
        direct = root / name
        return direct if direct.exists() else root / mapping.get(name, name)

    def check(condition, description):
        if not condition:
            raise AssertionError(description)
        passed.append(description)

    source = fixture('source.html').read_bytes()
    original = Page()
    original.feed(source.decode('utf-8-sig'))
    check(original.canonicals == [CANONICAL], 'Existing source has one slash canonical')
    check(original.h1s == ['Refrigeration Brands Same-Day Repair in London'], 'Existing page identity retained')
    check(bool(original.title), 'Existing title is present')
    check(bool(original.jsonld), 'Existing JSON-LD parses')
    check(all(ref.startswith(('/', '#')) or urlsplit(ref).scheme for ref in original.references), 'All assets and links retain their meaning in the new directory')

    for name in ('root-index.html', 'mirror-index.html'):
        content = fixture(name).read_bytes()
        check(content == source, name + ' exactly preserves existing source bytes')
        page = Page()
        page.feed(content.decode('utf-8-sig'))
        check(page.canonicals == original.canonicals, name + ' canonical retained')
        check(page.h1s == original.h1s and page.title == original.title, name + ' H1 and title retained')
        check(page.jsonld == original.jsonld, name + ' JSON-LD retained')

    for prefix in ('root', 'mirror'):
        before = directives(fixture(prefix + '-before.htaccess').read_text(encoding='utf-8-sig'))
        after = directives(fixture(prefix + '.htaccess').read_text(encoding='utf-8-sig'))
        check(after.count(EXPECTED_RULE) == 1, prefix + ' contains one exact index exemption')
        extra = after.copy()
        for line in before:
            extra.remove(line)
        extra.remove(EXPECTED_RULE)
        check(len(extra) == 5, prefix + ' exactly five additional alias redirects')
        check([line for line in after if line != EXPECTED_RULE and line not in extra] == before, prefix + ' all existing directives and ordering preserved')
        for slug, target in TARGETS.items():
            matches = [line for line in extra if re.fullmatch(line.split()[1], slug)]
            check(len(matches) == 1, prefix + ' single explicit redirect for ' + slug)
            tokens = matches[0].split()
            check(tokens[0] == 'RewriteRule' and tokens[2] == target and tokens[3] == '[R=301,L]', prefix + ' permanent correct target for ' + slug)
            check(all(re.fullmatch(tokens[1], other) is None for other in (slug + '/', slug + '.asp', slug + '.html', 'unrelated-repair-london', 'prefix-' + slug)), prefix + ' only exact bare alias matches for ' + slug)
            https_pos = next(i for i, line in enumerate(after) if 'https://%{HTTP_HOST}%{REQUEST_URI}' in line)
            pretty_pos = next(i for i, line in enumerate(after) if line.startswith(r'RewriteRule ^(.+?)/?$'))
            check(https_pos < after.index(matches[0]) < pretty_pos, prefix + ' alias ordered after HTTPS and before generic rewrite for ' + slug)
        exemption_pos = after.index(EXPECTED_RULE)
        generic_pos = next(i for i, line in enumerate(after) if line.startswith(r'RewriteRule ^(.*)\.html$'))
        check(exemption_pos < generic_pos, prefix + ' exact exemption precedes generic HTML redirect')
        pattern = EXPECTED_RULE.split()[1]
        check(re.fullmatch(pattern, SLUG + '/index.html') is not None, prefix + ' index path matches exemption')
        check(all(re.fullmatch(pattern, path) is None for path in (SLUG + '/', SLUG + '.html', 'brands/index.html', 'services/index.html', 'blog/commercial-fridge-repair-cost-london.html')), prefix + ' exemption does not broaden to other routes')
        check(any(r'^blog/commercial-fridge-repair-cost-london/$' in line and '[L]' in line for line in after), prefix + ' prior cost internal rewrite retained')
        check(any(r'^services/index\.html$' in line for line in after), prefix + ' Services exemption retained')

    config = ET.parse(fixture('web.config')).getroot()
    defaults = config.findall('./system.webServer/defaultDocument/files/add')
    check(bool(defaults) and defaults[0].get('value') == 'index.html', 'IIS already prefers index.html as directory default')
    rules = config.findall('./system.webServer/rewrite/rules/rule')
    for name in ('ASP Extensionless Root', 'ASP Extensionless Subfolder'):
        rule = next(rule for rule in rules if rule.get('name') == name)
        check(any(condition.get('matchType') == 'IsDirectory' and condition.get('negate') == 'true' for condition in rule.findall('./conditions/add')), name + ' bypasses existing physical directories')
    for after_name, before_name in (('web.config', 'web-before.config'), ('mirror-web.config', 'mirror-web-before.config')):
        after_config = ET.parse(fixture(after_name)).getroot()
        before_config = ET.parse(fixture(before_name)).getroot()
        after_rules = after_config.findall('./system.webServer/rewrite/rules/rule')
        before_rules = before_config.findall('./system.webServer/rewrite/rules/rule')
        before_names = {rule.get('name') for rule in before_rules}
        new_rules = [rule for rule in after_rules if rule.get('name') not in before_names]
        check(len(new_rules) == 2, after_name + ' exactly two new whitelist rules')
        brand_pos = next(i for i, rule in enumerate(after_rules) if rule.get('name') == 'Brand repair to fridge-repair')
        check(all(after_rules.index(rule) < brand_pos for rule in new_rules), after_name + ' whitelist before generic brand rewrite')
        for slug, target in TARGETS.items():
            matches = [rule for rule in new_rules if re.fullmatch(rule.find('match').get('url'), slug)]
            check(len(matches) == 1, after_name + ' one whitelist match for ' + slug)
            rule = matches[0]
            match = re.fullmatch(rule.find('match').get('url'), slug)
            action = rule.find('action')
            result = action.get('url')
            for i, value in enumerate(match.groups(), 1):
                result = result.replace('{R:' + str(i) + '}', value)
            check(result == target and action.get('type') == 'Redirect' and action.get('redirectType') == 'Permanent' and action.get('appendQueryString') == 'true' and rule.get('stopProcessing') == 'true', after_name + ' correct permanent query-preserving target for ' + slug)
            check(all(re.fullmatch(rule.find('match').get('url'), other) is None for other in (slug + '/', slug + '.asp', slug + '.html', 'unrelated-repair-london', 'prefix-' + slug)), after_name + ' excludes slash/extension/unrelated variants for ' + slug)
        parent_rules = after_config.find('./system.webServer/rewrite/rules')
        for rule in new_rules:
            parent_rules.remove(rule)
        check(xml_identity(after_config) == xml_identity(before_config), after_name + ' all existing XML nodes and order preserved')
    print(json.dumps({'passed': len(passed), 'checks': passed, 'scope': 'static source/configuration checks only; live server GET/HEAD and redirects remain required'}, indent=2))


if __name__ == '__main__':
    main()

