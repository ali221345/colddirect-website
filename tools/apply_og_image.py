#!/usr/bin/env python3
"""Idempotent post-freeze activator: add og:image + twitter:image to the homepage and the 9 core money pages.

    python tools/apply_og_image.py --check     # read-only: which files already carry the tags (exit 0 = all applied)
    python tools/apply_og_image.py             # apply (REFUSED before 2026-10-21T00:00:00Z - freeze lifted early by owner on 2026-10-21)
    python tools/apply_og_image.py --selftest  # offline tests in isolated temp directories (no repo file is touched)

Adds exactly two lines to every copy of every target page (root <slug>.html, root <slug>/index.html and the same two in
colddirect-public-html/, plus index.html in root and mirror):

    <meta property="og:image" content="https://www.colddirect.co.uk/images/og-colddirect-london.jpg">
    <meta name="twitter:image" content="https://www.colddirect.co.uk/images/og-colddirect-london.jpg">

Rules: nothing else in a file changes (title, h1, schema, every other tag stay byte-identical; the file's own line endings
and the anchor line's indentation are reused). The new lines go right after the last existing og:/twitter: meta tag, else
after <link rel="canonical">, else before </head>. A tag that already exists is left alone, so a re-run changes nothing.
Pages that ALREADY have their own page-specific og:image (today: commercial fridge / commercial freezer / fridge / freezer /
air conditioning / cellar) keep it (state KEPT, a missing twitter:image just mirrors that page's og:image) - the generic
homepage image is never forced over a more relevant one. Duplicate og:image / twitter:image tags are a CONFLICT: that file
is left completely untouched and the run exits 1.

Date guard: --force only works together with --root pointing at an isolated directory (unit tests); it can never bypass the
freeze on the real repository. The 1200x630 JPEG must exist (tools/make_og_image.py) or nothing is written.
auto-seo.aspx needs no change: it owns only title / meta description / keywords / V4 blocks / alt text / sitemap and contains
no og: or twitter: logic, so it neither strips nor rewrites these tags (--check prints this verification).

Exit codes: 0 ok / nothing to do, 1 pending or conflict (check) / problem, 2 refused by the guard.
"""
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.dirname(HERE)

IMG_URL = "https://www.colddirect.co.uk/images/og-colddirect-london.jpg"
IMG_REL = os.path.join("images", "og-colddirect-london.jpg")
OG_TAG = '<meta property="og:image" content="%s">' % IMG_URL
TW_TAG = '<meta name="twitter:image" content="%s">' % IMG_URL
FREEZE_END = datetime(2026, 10, 21, 0, 0, 0, tzinfo=timezone.utc)
CORE = [
    "commercial-fridge-repair-london", "commercial-freezer-repair-london", "cold-room-repair-london",
    "fridge-repair-london", "freezer-repair-london", "catering-repair-london",
    "commercial-appliances-repair-london", "air-conditioning-repair-london", "cellar-cooler-repair-london",
]
MIRROR_DIR = "colddirect-public-html"

_META_RE = re.compile(r"<meta\b[^>]*>", re.I)
_ATTR_RE = re.compile(r"""([^\s=/>"']+)\s*=\s*("[^"]*"|'[^']*'|[^\s"'>]+)""")


def target_files(root):
    """Every HTML copy that must carry the tags: (relative path, ...) for root + mirror."""
    rels = ["index.html"]
    for slug in CORE:
        rels += ["%s.html" % slug, os.path.join(slug, "index.html")]
    out = []
    for base in ("", MIRROR_DIR):
        out += [os.path.join(base, r) if base else r for r in rels]
    return out


def _attrs(tag):
    return {k.lower(): v.strip("\"'") for k, v in _ATTR_RE.findall(tag)}


def _find(text, kind):
    """Existing image meta tags of kind 'og' (property=og:image) or 'tw' (name|property=twitter:image): [(match, content)]."""
    found = []
    for m in _META_RE.finditer(text):
        a = _attrs(m.group(0))
        if kind == "og" and a.get("property", "").lower() == "og:image":
            found.append((m, a.get("content", "")))
        if kind == "tw" and (a.get("name") or a.get("property") or "").lower() == "twitter:image":
            found.append((m, a.get("content", "")))
    return found


def plan(text):
    """Inspect one HTML document. Returns (to_add [tag strings], conflicts [str], kept [str]).

    * no og:image -> add ours; no twitter:image -> add one that mirrors the page's og:image URL
    * an existing single og:image / twitter:image (even a different, page-specific image) is KEPT as is, never overwritten
    * duplicate og:image / twitter:image tags are a CONFLICT (page left completely untouched)
    """
    add, conflicts, kept = [], [], []
    og, tw = _find(text, "og"), _find(text, "tw")
    for found, label in ((og, "og:image"), (tw, "twitter:image")):
        if len(found) > 1:
            conflicts.append("%s duplicated (%s)" % (label, " / ".join(c or "<empty>" for _, c in found)))
    if conflicts:
        return [], conflicts, []
    og_url = og[0][1] if og else IMG_URL
    if not og:
        add.append(OG_TAG)
    elif og_url != IMG_URL:
        kept.append("og:image " + og_url.replace("https://www.colddirect.co.uk", ""))
    if not tw:
        add.append('<meta name="twitter:image" content="%s">' % og_url)
    elif tw[0][1] != IMG_URL and tw[0][1] != og_url:
        kept.append("twitter:image " + tw[0][1].replace("https://www.colddirect.co.uk", ""))
    return add, conflicts, kept


def inject(text, tags):
    """Insert `tags` (list of strings) after the last og:/twitter: meta, else after canonical, else before </head>.
    Reuses the file's line ending and the anchor line's indentation; nothing else is modified."""
    if not tags:
        return text
    eol = "\r\n" if "\r\n" in text else "\n"
    anchor = None
    for m in _META_RE.finditer(text):
        a = _attrs(m.group(0))
        if (a.get("property") or a.get("name") or "").lower().startswith(("og:", "twitter:")):
            anchor = m
    if anchor is None:
        for m in re.finditer(r"<link\b[^>]*>", text, re.I):
            if "canonical" in _attrs(m.group(0)).get("rel", "").lower().split():
                anchor = m
                break
    if anchor is not None:
        line_start = text.rfind("\n", 0, anchor.start()) + 1
        indent = re.match(r"[ \t]*", text[line_start:anchor.start()]).group(0)
        if text[line_start:anchor.start()].strip():
            indent = ""                                   # anchor shares its line with other markup
        insert_at = anchor.end()
        return text[:insert_at] + "".join(eol + indent + t for t in tags) + text[insert_at:]
    m = re.search(r"</head\s*>", text, re.I)
    if not m:
        raise ValueError("no <head> end found")
    return text[:m.start()] + "".join("  " + t + eol for t in tags) + text[m.start():]


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def image_ok(root):
    """The 1200x630 JPEG exists in root (and mirror when the mirror dir exists)."""
    import make_og_image as mk
    problems = []
    for base in ("", MIRROR_DIR):
        d = os.path.join(root, base) if base else root
        if base and not os.path.isdir(d):
            continue
        p = os.path.join(d, IMG_REL)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            problems.append("%s missing or empty" % os.path.join(base, IMG_REL))
        elif mk.jpeg_size(p) != (mk.W, mk.H):
            problems.append("%s is not a %dx%d JPEG" % (os.path.join(base, IMG_REL), mk.W, mk.H))
    return problems


def audit(root):
    """Read-only. Returns {rel: ('applied'|'pending'|'conflict'|'absent', detail)}."""
    res = {}
    for rel in target_files(root):
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            res[rel] = ("absent", "file not found")
            continue
        add, conflicts, kept = plan(read(p))
        if conflicts:
            res[rel] = ("conflict", "; ".join(conflicts))
        elif add:
            res[rel] = ("pending", "missing " + ", ".join("og:image" if "og:" in t else "twitter:image" for t in add))
        elif kept:
            res[rel] = ("kept", "page-specific " + "; ".join(kept))
        else:
            res[rel] = ("applied", "")
    return res


def guard(root, now, force):
    """Returns None when allowed, else the refusal text."""
    if now >= FREEZE_END:
        return None
    isolated = os.path.realpath(root) != os.path.realpath(REPO)
    if force and isolated:
        return None
    why = ("--force is only honoured together with --root pointing at an isolated temp directory (unit tests); "
           "it can never bypass the freeze on the real repository" if force else "")
    return "REFUSED: SEO content freeze active until %s (now %s). %s" % (
        FREEZE_END.strftime("%Y-%m-%dT%H:%M:%SZ"), now.strftime("%Y-%m-%dT%H:%M:%SZ"), why)


def apply(root, now=None, force=False, log=print):
    """Apply to every target. Returns (exit_code, changed_files)."""
    now = now or datetime.now(timezone.utc)
    refusal = guard(root, now, force)
    if refusal:
        log(refusal)
        return 2, []
    probs = image_ok(root)
    if probs:
        log("REFUSED: social image not ready (" + "; ".join(probs) + ") - run tools/make_og_image.py first")
        return 2, []
    changed, conflicts, absent = [], [], []
    for rel in target_files(root):
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            absent.append(rel)
            continue
        text = read(p)
        add, conf, _kept = plan(text)
        if conf:
            conflicts.append("%s: %s" % (rel, "; ".join(conf)))
            continue                                      # a conflicting page is left completely untouched
        if add:
            new = inject(text, add)
            write(p, new)
            changed.append(rel)
    log("og:image activator: %d file(s) changed, %d already up to date / kept, %d absent, %d conflict(s)" % (
        len(changed), len(target_files(root)) - len(changed) - len(absent) - len(conflicts), len(absent), len(conflicts)))
    for c in conflicts:
        log("  CONFLICT (left untouched): " + c)
    for a in absent:
        log("  absent: " + a)
    return (1 if conflicts else 0), changed


def aspx_note(root):
    p = os.path.join(root, "auto-seo.aspx")
    if not os.path.isfile(p):
        return "auto-seo.aspx not found"
    t = read(p).lower()
    if "og:" in t or "twitter:" in t:
        return "auto-seo.aspx contains og:/twitter: logic - review it"
    return "auto-seo.aspx contains no og:/twitter: logic: it preserves these tags (no change needed)"


def check(root, log=print):
    res = audit(root)
    counts = {}
    for rel, (state, detail) in res.items():
        counts[state] = counts.get(state, 0) + 1
        if state != "applied":
            log("  %-8s %s %s" % (state.upper(), rel, ("(" + detail + ")") if detail else ""))
    img = image_ok(root)
    log("social image: " + ("OK (1200x630 JPEG present)" if not img else "; ".join(img)))
    log(aspx_note(root))
    log("og:image check: %d applied, %d kept (page-specific image already set), %d pending, %d conflict, %d absent (of %d files)" % (
        counts.get("applied", 0), counts.get("kept", 0), counts.get("pending", 0), counts.get("conflict", 0),
        counts.get("absent", 0), len(res)))
    bad = counts.get("pending", 0) or counts.get("conflict", 0) or counts.get("absent", 0) or img
    return 1 if bad else 0


# ------------------------------------------------------------------ self-test (isolated temp dirs only)
def selftest():
    import make_og_image as mk
    PAST = datetime(2026, 10, 20, 3, 0, tzinfo=timezone.utc)
    ENDS = datetime(2026, 10, 21, 0, 0, 0, tzinfo=timezone.utc)
    LATER = datetime(2026, 10, 21, 7, 0, tzinfo=timezone.utc)
    HEAD = ('<!DOCTYPE html>\n<html lang="en-GB">\n<head>\n  <meta charset="utf-8">\n  <title>Cold Room &amp; More | ColdDirect</title>\n'
            '  <meta property="og:title" content="Cold Room">\n  <meta property="og:description" content="Desc">\n'
            '  <link rel="canonical" href="https://www.colddirect.co.uk/%s">\n  <style>a{b:c}</style>\n</head>\n'
            '<body><h1>Cold Room Repair London</h1></body></html>\n')

    def jpeg_bytes():
        from PIL import Image
        import io
        b = io.BytesIO()
        Image.new("RGB", (mk.W, mk.H), (10, 80, 140)).save(b, "JPEG")
        return b.getvalue()

    def build(td, mutate=None):
        jpg = jpeg_bytes()
        for base in ("", MIRROR_DIR):
            d = os.path.join(td, base) if base else td
            os.makedirs(os.path.join(d, "images"), exist_ok=True)
            open(os.path.join(d, IMG_REL), "wb").write(jpg)
            for rel in target_files(td)[:len(target_files(td)) // 2]:       # the 19 root-relative names
                p = os.path.join(d, rel)
                os.makedirs(os.path.dirname(p) or d, exist_ok=True)
                slug = os.path.basename(os.path.dirname(rel)) if rel.endswith("index.html") and os.path.dirname(rel) else rel[:-5]
                write(p, HEAD % ("" if rel == "index.html" else slug + "/"))
        if mutate:
            mutate(td)

    def snapshot(td):
        out = {}
        for rel in target_files(td):
            p = os.path.join(td, rel)
            if os.path.isfile(p):
                out[rel] = open(p, "rb").read()
        return out

    logs = []
    log = logs.append
    n_targets = 1 + 2 * len(CORE)                       # 19 per tree
    assert len(target_files(REPO)) == 2 * n_targets == 38

    # 1. date guard: before the freeze ends nothing is written, with or without --force on a "real" root
    with tempfile.TemporaryDirectory() as td:
        build(td)
        before = snapshot(td)
        for t in (PAST, datetime(2026, 10, 20, 23, 59, 59, tzinfo=timezone.utc)):
            code, ch = apply(td, now=t, force=False, log=log)
            assert code == 2 and ch == [] and snapshot(td) == before, (t, code)
        assert any("REFUSED: SEO content freeze active until 2026-10-21T00:00:00Z" in l for l in logs)
        # --force on the REAL repository root can never pass (checked without touching the repo: guard only)
        assert guard(REPO, PAST, True) is not None and "never bypass" in guard(REPO, PAST, True)
        assert guard(REPO, PAST, False) is not None and guard(REPO, ENDS, False) is None
        # --force on an isolated temp root is allowed (this is the unit-test mode)
        assert guard(td, PAST, True) is None and guard(td, PAST, False) is not None
        # missing / wrong-size image blocks even after the freeze
        os.remove(os.path.join(td, IMG_REL))
        code, ch = apply(td, now=LATER, log=log)
        assert code == 2 and ch == [] and snapshot(td) == before
        open(os.path.join(td, IMG_REL), "wb").write(b"not a jpeg")
        assert apply(td, now=LATER, log=log)[0] == 2 and snapshot(td) == before

    # 2. apply: exactly the two tags are added to all 38 files; everything else byte-identical; re-run = no change
    with tempfile.TemporaryDirectory() as td:
        build(td)
        before = snapshot(td)
        st = audit(td)
        assert all(v[0] == "pending" for v in st.values()) and len(st) == 38
        assert check(td, log=log) == 1
        code, changed = apply(td, now=PAST, force=True, log=log)            # isolated temp dir + --force
        assert code == 0 and len(changed) == 38, (code, len(changed))
        after = snapshot(td)
        for rel, new in after.items():
            old = before[rel].decode()
            new = new.decode()
            assert new.count(OG_TAG) == 1 and new.count(TW_TAG) == 1, rel
            removed = new.replace("\n  " + OG_TAG, "", 1).replace("\n  " + TW_TAG, "", 1)
            assert removed == old, rel                                       # nothing but the two inserted lines changed
            assert re.search(r"<title>[^<]*</title>", new).group(0) == re.search(r"<title>[^<]*</title>", old).group(0)
            assert re.search(r"<h1>[^<]*</h1>", new).group(0) == re.search(r"<h1>[^<]*</h1>", old).group(0)
            # placed after the last og meta (og:description), before canonical
            assert new.index('og:description') < new.index(OG_TAG) < new.index(TW_TAG) < new.index('rel="canonical"'), rel
        assert all(v[0] == "applied" for v in audit(td).values()) and check(td, log=log) == 0
        code, changed2 = apply(td, now=LATER, log=log)                       # second run: idempotent
        assert code == 0 and changed2 == [] and snapshot(td) == after

    # 3. canonical-only anchor, no-canonical (before </head>), CRLF files, foreign / duplicate tags, absent files
    with tempfile.TemporaryDirectory() as td:
        build(td)
        crlf = os.path.join(td, "index.html")
        write(crlf, HEAD.replace("\n", "\r\n") % "")
        nocanon = os.path.join(td, "cold-room-repair-london.html")
        write(nocanon, "<html><head><title>T</title></head><body><h1>H</h1></body></html>\n")
        canon_only = os.path.join(td, "fridge-repair-london.html")
        write(canon_only, '<html><head>\n\t<title>T</title>\n\t<link rel="canonical" href="https://www.colddirect.co.uk/fridge-repair-london/">\n</head><body><h1>H</h1></body></html>\n')
        foreign = os.path.join(td, "freezer-repair-london.html")
        t = read(foreign).replace('<meta property="og:title"', '<meta property="og:image" content="https://example.com/other.jpg">\n  <meta property="og:title"')
        write(foreign, t)
        half = os.path.join(td, "catering-repair-london.html")             # og:image already right, twitter missing, single quotes
        write(half, read(half).replace('<meta property="og:title"', "<meta property='og:image' content='%s'>\n  <meta property=\"og:title\"" % IMG_URL))
        dup = os.path.join(td, "catering-repair-london", "index.html")
        write(dup, read(dup).replace('<meta property="og:title"', OG_TAG + '\n  ' + OG_TAG + '\n  <meta property="og:title"'))
        os.remove(os.path.join(td, "air-conditioning-repair-london.html"))
        st = audit(td)
        assert st["air-conditioning-repair-london.html"][0] == "absent"
        assert st["freezer-repair-london.html"] == ("pending", "missing twitter:image")      # foreign og:image is kept
        both = os.path.join(td, "cellar-cooler-repair-london.html")                          # page-specific og + twitter
        write(both, read(both).replace('<meta property="og:title"',
                                       '<meta property="og:image" content="https://www.colddirect.co.uk/images/pub-cellar.webp">\n'
                                       '  <meta name="twitter:image" content="https://www.colddirect.co.uk/images/pub-cellar.webp">\n  <meta property="og:title"'))
        st = audit(td)
        assert st["cellar-cooler-repair-london.html"][0] == "kept" and "/images/pub-cellar.webp" in st["cellar-cooler-repair-london.html"][1]
        both_before = read(both)
        assert st[os.path.join("catering-repair-london", "index.html")][0] == "conflict"       # duplicate og:image
        assert st["catering-repair-london.html"][0] == "pending" and "twitter:image" in st["catering-repair-london.html"][1]
        before = snapshot(td)
        code, changed = apply(td, now=LATER, log=log)
        assert code == 1                                                    # conflicts reported, never overwritten
        after = snapshot(td)
        f = after["freezer-repair-london.html"].decode()
        assert "example.com/other.jpg" in f and OG_TAG not in f and f.count("og:image") == 1
        assert f.count('<meta name="twitter:image" content="https://example.com/other.jpg">') == 1     # mirrors the page's og:image
        assert read(both) == both_before                                                              # kept page: untouched
        assert after[os.path.join("catering-repair-london", "index.html")] == before[os.path.join("catering-repair-london", "index.html")]
        # CRLF preserved: every line break in the file is still CRLF, tags inserted with CRLF
        c = after["index.html"].decode()
        assert "\n" not in c.replace("\r\n", "") and c.count(OG_TAG) == 1 and ("\r\n  " + OG_TAG) in c
        # no canonical -> inserted right before </head>, title / h1 untouched
        n = after["cold-room-repair-london.html"].decode()
        assert n == "<html><head><title>T</title>  %s\n  %s\n</head><body><h1>H</h1></body></html>\n" % (OG_TAG, TW_TAG), n
        # canonical-only -> after the canonical link with its tab indentation
        k = after["fridge-repair-london.html"].decode()
        assert ('/fridge-repair-london/">\n\t' + OG_TAG + "\n\t" + TW_TAG + "\n</head>") in k, k
        # half-applied page gets only the missing twitter tag
        h = after["catering-repair-london.html"].decode()
        assert h.count("og:image") == 1 and h.count(TW_TAG) == 1 and "content='%s'" % IMG_URL in h
        assert check(td, log=log) == 1

    # 4. real repository: read-only facts only (nothing is written)
    assert IMG_URL.endswith("/images/og-colddirect-london.jpg") and OG_TAG.startswith('<meta property="og:image"') and TW_TAG.startswith('<meta name="twitter:image"')
    assert not [l for l in logs if "private_key" in l]
    print("selftest OK (date guard: refused before 2026-10-21 incl. --force on the real repo; image prerequisite; "
          "38 files get exactly 2 inserted lines, title/h1/other bytes unchanged; idempotent re-run; CRLF + indentation kept; "
          "canonical / no-canonical anchors; foreign + duplicate tags reported not overwritten; --check exit codes)")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()
    root = REPO
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    if "--check" in argv:
        return check(root)
    code, _ = apply(root, force="--force" in argv)
    return code


if __name__ == "__main__":
    sys.exit(main())
