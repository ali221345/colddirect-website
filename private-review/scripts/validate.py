from pathlib import Path
from lxml import html
from urllib.parse import urlsplit, unquote
import json, re

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
errors=[]
pages=list(DIST.rglob('*.html'))
references=0

def resolve(page, url):
 u=urlsplit(url)
 if u.scheme or u.netloc or not u.path: return None
 path=unquote(u.path)
 target=DIST/path.lstrip('/') if path.startswith('/') else page.parent/path
 if target.is_dir():target=target/'index.html'
 elif not target.exists() and not target.suffix:
  if target.with_suffix('.html').exists():target=target.with_suffix('.html')
 return target

for page in pages:
 text=page.read_text()
 tree=html.document_fromstring(text)
 rel=str(page.relative_to(DIST))
 if len(tree.xpath('//h1'))!=1:errors.append([rel,'Expected one H1',len(tree.xpath('//h1'))])
 if len(tree.xpath('//main[@id="main-content"]'))!=1:errors.append([rel,'Missing single main landmark'])
 if len(tree.xpath('//header[@class="review-header"]'))!=1:errors.append([rel,'Missing shared header'])
 if not tree.xpath('//meta[@name="robots" and @content="noindex, nofollow"]'):errors.append([rel,'Missing noindex'])
 if not tree.xpath('//meta[@name="viewport"]'):errors.append([rel,'Missing viewport'])
 if not tree.xpath('//title/text()') or not tree.xpath('//meta[@name="description"]/@content'):errors.append([rel,'Missing metadata'])
 ids=tree.xpath('//*[@id]/@id')
 if len(ids)!=len(set(ids)):errors.append([rel,'Duplicate IDs'])
 if '<!--#include' in text or 'booking.asp' in text:errors.append([rel,'Unresolved server dependency'])
 for el in tree.xpath('//a[@href] | //img[@src] | //script[@src] | //link[@href]'):
  url=el.get('src') or el.get('href');target=resolve(page,url)
  if target is not None:
   references+=1
   if not target.exists():errors.append([rel,'Missing local target',url])
  if el.tag=='a' and url.startswith('#') and url[1:] and not tree.xpath('//*[@id=$id]',id=url[1:]):errors.append([rel,'Missing anchor',url])
 for img in tree.xpath('//img'):
  if img.get('alt') is None:errors.append([rel,'Image without alt'])
 for form in tree.xpath('//form'):
  if form.get('action'):errors.append([rel,'Unexpected network form action'])
  for field in form.xpath('.//input | .//textarea | .//select'):
   if not field.get('id') or not tree.xpath('//label[@for=$id]',id=field.get('id')):errors.append([rel,'Form field without label',field.get('id')])
 css=(DIST/'assets/review.css').read_text()

required=['index.html','services/index.html','contact/index.html','coverage/index.html','about-us/index.html','brands/index.html','faqs/index.html','blog/index.html','commercial-fridge-repair-london/index.html','commercial-freezer-repair-london/index.html','cold-room-repair-london/index.html','ice-machine-repair-london/index.html','commercial-refrigeration-servicing-london/index.html']
for key in required:
 if not (DIST/key).exists():errors.append([key,'Required route missing'])
if list(DIST.rglob('*.asp')) or list(DIST.rglob('*.php')):errors.append(['dist','Server source should not be deployed statically'])
if (DIST/'robots.txt').read_text()!='User-agent: *\nDisallow: /\n':errors.append(['robots.txt','Invalid private review policy'])
if not all(rule in css for rule in ['@media(max-width:640px)','@media(max-width:900px)','@media(max-width:1100px)','prefers-reduced-motion','safe-area-inset-bottom','minmax(0,1fr)']):errors.append(['CSS','Missing responsive/accessibility rules'])
result={'pages_checked':len(pages),'local_references_checked':references,'key_routes':len(required),'errors':errors}
print(json.dumps(result,indent=2))
raise SystemExit(bool(errors))
