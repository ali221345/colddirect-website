"""Independent limited rewrite simulation, NOT Apache/IIS or live-server proof.

Models ordered RewriteRule, the present file/directory/HTTPS conditions, [L],
301 redirects, query preservation and per-directory rewrite re-entry. Uses an
explicit synthetic public filesystem. Does not model mod_alias RedirectMatch,
DirectoryIndex subrequests, IIS translation, SSI, PHP, caches or hosting HTTPS.
Also proves all non-cost directives are unchanged in each prepared configuration.
"""
from pathlib import Path
import argparse
import json
import re
from urllib.parse import urlsplit, urlunsplit

BASE = Path(__file__).resolve().parents[1]
COST = 'blog/commercial-fridge-repair-cost-london'
FILES = {
    COST + '.html', 'index.html', 'index.php', 'services/index.html',
    'blog/index.html', 'blog/different-types-of-ice.html', 'google123.html',
    'blog/commercial-freezer-ice-buildup-causes/index.html',
    'blog/cold-room-temperature-fluctuation/index.html',
    'blog/commercial-fridge-not-cooling/index.html',
    'fridge-repair-london/index.html', 'freezer-repair-london/index.html',
    'commercial-fridge-repair-london/index.html',
    'cold-room-repair-north-london/index.html',
}
DIRS = {''} | {f.rsplit('/', 1)[0] for f in FILES if '/' in f}


def directives(text):
    return [line.strip() for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith('#')]


def rules(text):
    result, pending = [], []
    for line in directives(text):
        if line.startswith('RewriteCond '):
            _, value, condition = line.split(maxsplit=2)
            pending.append((value, condition))
        elif line.startswith('RewriteRule '):
            fields = line.split()
            flags = fields[3].strip('[]').split(',') if len(fields) > 3 else []
            result.append((re.compile(fields[1]), fields[2], flags, pending))
            pending = []
    assert not pending
    return result


def expand(value, match):
    return re.sub(r'\$(\d)', lambda m: match.group(int(m[1])) or '', value)


def conditions_pass(conditions, match, path, scheme):
    for value, condition in conditions:
        if value == '%{HTTPS}':
            ok = ('on' if scheme == 'https' else 'off') == condition
        else:
            if value == '%{REQUEST_FILENAME}':
                filename = path
            elif value.startswith('%{DOCUMENT_ROOT}/'):
                filename = expand(value[len('%{DOCUMENT_ROOT}/'):], match)
            else:
                raise AssertionError('Unsupported simulation variable: ' + value)
            if condition in ('-f', '!-f'):
                ok = filename in FILES
            elif condition in ('-d', '!-d'):
                ok = filename.rstrip('/') in DIRS
            else:
                raise AssertionError('Unsupported simulation condition: ' + condition)
            if condition.startswith('!'):
                ok = not ok
        if not ok:
            return False
    return True


def request(parsed_rules, url):
    parts = urlsplit(url)
    path = parts.path.lstrip('/')
    seen = set()
    for _ in range(30):
        if path in seen:
            return {'status': 'internal-cycle', 'served': path}
        seen.add(path)
        rewritten = False
        for regex, target, flags, conditions in parsed_rules:
            match = regex.search(path)
            if not match or not conditions_pass(conditions, match, path, parts.scheme):
                continue
            if target == '-':
                return {'status': 200 if path in FILES or path.rstrip('/') in DIRS else 404,
                        'served': path}
            replacement = expand(target, match)
            replacement = replacement.replace('%{HTTP_HOST}', parts.netloc)
            replacement = replacement.replace('%{REQUEST_URI}', '/' + path)
            if any(flag.startswith('R=') for flag in flags):
                target_parts = urlsplit(replacement)
                location = urlunsplit((target_parts.scheme or parts.scheme,
                    target_parts.netloc or parts.netloc, target_parts.path,
                    target_parts.query or parts.query, ''))
                return {'status': 301, 'location': location}
            path = replacement.lstrip('/')
            rewritten = True
            # All rewriting rules in these configs end in L; re-enter root rules.
            assert 'L' in flags
            break
        if not rewritten:
            return {'status': 200 if path in FILES or path.rstrip('/') in DIRS else 404,
                    'served': path}
    return {'status': 'internal-limit', 'served': path}


def chain(parsed_rules, url):
    seen, responses = set(), []
    for _ in range(15):
        if url in seen:
            return {'status': 'external-cycle', 'responses': responses}
        seen.add(url)
        response = request(parsed_rules, url)
        responses.append(response)
        if response['status'] != 301:
            return {'status': response['status'], 'responses': responses}
        url = response['location']
    return {'status': 'external-limit', 'responses': responses}


def check(base):
    checks = 0
    comparison_paths = ['/', '/services/', '/services', '/services/index.html',
        '/services.html', '/fridge-repair-london/', '/freezer-repair-london/',
        '/commercial-fridge-repair-london/', '/cold-room-repair-north-london/',
        '/fridge-repairs-london', '/freezer-repairs-london.html',
        '/commercial-fridge-repairs-london.asp', '/google123.html',
        '/blog/', '/blog/index.html', '/blog/different-types-of-ice/',
        '/blog/commercial-freezer-ice-buildup-causes/',
        '/blog/cold-room-temperature-fluctuation/',
        '/blog/commercial-fridge-not-cooling/', '/blog/unknown-old-slug/',
        '/blog/commercial-fridge-repair-cost-london-extra/',
        '/blog/COMMERCIAL-FRIDGE-REPAIR-COST-LONDON/',
        '/blog/commercial-fridge-repair-cost-london.html/']
    for name in ['root', 'mirror']:
        before_path = base / ('before-' + name + '.htaccess')
        if not before_path.exists():
            before_path = base / 'tools/fixtures/repair-cost-routing' / ('before-' + name + '.htaccess')
        before = before_path.read_text(encoding='utf-8')
        after_path = base / (name + '.htaccess')
        if not after_path.exists():
            after_path = base / ('.htaccess' if name == 'root' else 'colddirect-public-html/.htaccess')
        after = after_path.read_text(encoding='utf-8')
        before_other = [s for s in directives(before) if COST not in s]
        after_other = [s for s in directives(after) if COST not in s]
        assert before_other == after_other, name + ': unrelated directives changed'
        checks += 1
        old, new = rules(before), rules(after)
        for suffix in ['/', '.html', '']:
            for query in ['', '?probe=1', '?probe=a%2Fb&x=2']:
                url = 'https://www.colddirect.co.uk/' + COST + suffix + query
                old_chain = chain(old, url)
                assert old_chain['status'] == 'external-cycle', old_chain
                actual = chain(new, url)
                assert actual['status'] == 200, actual
                assert actual['responses'][-1]['served'] == COST + '.html'
                assert len(actual['responses']) == (2 if suffix == '' else 1), actual
                if suffix == '':
                    assert actual['responses'][0]['location'] == (
                        'https://www.colddirect.co.uk/' + COST + '/' + query)
                checks += 1
        # Existing behavior may itself contain defects. Preserve it, don't assert 200.
        for path in comparison_paths:
            for scheme in ['http', 'https']:
                for query in ['', '?probe=1&x=a%2Fb']:
                    url = scheme + '://www.colddirect.co.uk' + path + query
                    assert chain(old, url) == chain(new, url), name + ': changed ' + url
                    checks += 1
    print(json.dumps({'checks_passed': checks,
        'scope': 'Exact non-cost directives preserved; cost loop reproduced before and removed after',
        'validation': 'Limited synthetic rewrite simulation; not server proof',
        'live_checks_required': ['GET and HEAD with fresh query', 'canonical and correct article',
            'HTTP-to-HTTPS hosting policy', 'directory blogs and Services after deployment'],
        'http_caveat': 'Early article rules precede force-HTTPS; verify hosting-level enforcement'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=BASE,
        help='Directory containing root.htaccess, mirror.htaccess and before-root/before-mirror.htaccess')
    check(parser.parse_args().directory.resolve())

