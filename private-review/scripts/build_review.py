from pathlib import Path
from lxml import html, etree
from urllib.parse import urlsplit, urlunsplit
import shutil, json, re, os
from html import escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('COLDDIRECT_SOURCE', str(ROOT.parent)))
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)
shutil.copytree(SOURCE/'images',DIST/'images',dirs_exist_ok=True)
(DIST/'assets').mkdir(exist_ok=True)
shutil.copy2(ROOT/'site.css',DIST/'assets/review.css')
shutil.copy2(ROOT/'site.js',DIST/'assets/review.js')
for name in ['favicon.ico']:
 if (SOURCE/name).exists(): shutil.copy2(SOURCE/name,DIST/name)

SERVICES = [
 ('Commercial fridge repair','commercial-fridge-repair-london','Uprights, preparation counters and undercounter fridges for busy commercial kitchens.','fridge/commercial-fridge-kitchen-london.webp','kitchen'),
 ('Commercial freezer repair','commercial-freezer-repair-london','Upright and chest freezers, frozen display cabinets and catering equipment.','slider-colour-freezer.webp','kitchen'),
 ('Cold room repair','cold-room-repair-london','Walk-in chillers for restaurants, hotels, butchers and production kitchens.','cold-room-repair-london.webp','rooms'),
 ('Ice machine repair','ice-machine-repair-london','Commercial ice makers for bars, restaurants and hotels, including Hoshizaki.','ice-machine-repair-london-hero.webp','specialist'),
 ('Display cabinet repair','display-cabinet-repair-london','Serve-over counters, multideck displays and glass-door shop refrigeration.','display-cabinets.webp','kitchen'),
 ('Cellar cooling repair','cellar-cooler-repair-london','Cooling systems for beer cellars and storage areas in pubs, bars and venues.','pub-cellar.webp','specialist'),
 ('Freezer room repair','freezer-room-repair-london','Walk-in freezer rooms for commercial kitchens, wholesale and frozen storage.','freezer-room-repair-london.webp','rooms'),
 ('Bottle cooler repair','bottle-cooler-repair-london','Back-bar bottle coolers and commercial drinks cabinets for hospitality.','bottle-cooler-repair.webp','specialist'),
 ('Wine cooler repair','wine-cooler-repair-london','Commercial wine cabinets and storage cooling for restaurants and hotels.','wine-cooler-repair.webp','specialist'),
 ('Chiller repair','chiller-repair-london','Air-cooled, water and process chillers used by commercial businesses.','chiller-repair-london.webp','specialist'),
 ('Blast chiller repair','blast-chiller-repair-london','Commercial blast chilling equipment for catering and production kitchens.','blast-chiller-repair-london-new.webp','kitchen'),
 ('Ice cream machine repair','ice-cream-machine-repair-london','Soft-serve machines and batch freezers for commercial ice cream businesses.','ice-cream/technician-repair.webp','specialist'),
 ('Supermarket fridge repair','supermarket-fridge-repair-london','Retail multidecks, dairy cabinets and other shop refrigeration equipment.','multideck-display-london.webp','kitchen'),
 ('Commercial air conditioning','air-conditioning-repair-london','Split and VRF air conditioning repair for restaurants, takeaways and shops.','slider-colour-ac.webp','specialist'),
 ('Planned maintenance','commercial-refrigeration-servicing-london','Agreed inspections and servicing for commercial fridges, freezers and cold rooms.','pro/commercial-kitchen-cold-room.webp','maintenance'),
]

def card(service):
 title,slug,description,image,category = service
 if not (DIST/'images'/image).exists(): image='commercial-refrigeration-kitchen-20261014.webp'
 return f'''<a class="service-card" data-service-card data-category="{category}" href="/{slug}/"><img src="/images/{image}" alt="Illustrative {escape(title.lower())} equipment" width="800" height="450" loading="lazy" decoding="async"><div class="service-card-body"><h3>{title}</h3><p>{description}</p><span class="card-link">Explore service <span aria-hidden="true">↗</span></span></div></a>'''

def header(active=''):
 nav=[('Services','/services/'),('Maintenance','/commercial-refrigeration-servicing-london/'),('Coverage','/coverage/'),('About','/about-us/'),('Contact','/contact/')]
 links=''.join(f'<a href="{url}"'+(' aria-current="page"' if active==url else '')+f'>{name}</a>' for name,url in nav)
 return f'''<a class="skip-link" href="#main-content">Skip to content</a>
 <div class="review-bar"><div class="wrap"><span><span class="status-dot" aria-hidden="true"></span>24/7 emergency refrigeration support</span><span class="bar-secondary">Commercial businesses · London &amp; surrounding areas</span><a href="tel:+447983759320">07983 759320</a></div></div>
 <header class="review-header"><div class="wrap header-inner"><a class="brand" href="/" aria-label="ColdDirect home"><img src="/images/logo/colddirect-main.webp" alt="ColdDirect" width="1200" height="675"></a><button type="button" class="menu-toggle" aria-controls="review-navigation" aria-expanded="false">Menu</button><nav class="review-nav" id="review-navigation" aria-label="Main navigation">{links}</nav><a class="header-call" href="tel:+442039524822">Call 020 3952 4822</a></div></header>'''

def footer():
 return '''<section class="review-cta"><div class="wrap"><div><h2>Cooling problem? Let's get it sorted.</h2><p>Tell us your postcode, equipment and fault. We'll confirm availability.</p></div><a class="button" href="tel:+447983759320">Call 07983 759320 <span aria-hidden="true">↗</span></a></div></section>
 <footer class="review-footer"><div class="wrap"><div class="footer-grid"><div><div class="footer-wordmark">COLD<span>DIRECT</span></div><p>Commercial refrigeration repair<br>and planned maintenance.<br>Based in Enfield. Working across London.</p><p>27 Felixstowe Road<br>Enfield, London N9 0DX</p></div><div><h3>Services</h3><div class="footer-links"><a href="/commercial-fridge-repair-london/">Fridge &amp; freezer repair</a><a href="/cold-room-repair-london/">Cold rooms</a><a href="/ice-machine-repair-london/">Ice machines</a><a href="/commercial-refrigeration-servicing-london/">Planned maintenance</a><a href="/services/">All services</a></div></div><div><h3>Explore</h3><div class="footer-links"><a href="/about-us/">About ColdDirect</a><a href="/coverage/">Areas we cover</a><a href="/brands/">Brands we repair</a><a href="/blog/">Advice &amp; guides</a><a href="/faqs/">FAQs</a><a href="/contact/">Contact us</a></div></div><div><h3>Talk to the team</h3><div class="footer-links"><a href="tel:+447983759320">07983 759320 · Emergency</a><a href="tel:+442039524822">020 3952 4822 · London</a><a href="tel:+448001123427">0800 112 3427 · Freephone</a><a href="mailto:info@colddirect.co.uk">info@colddirect.co.uk</a><a href="/contact/">Prepare an enquiry →</a></div></div></div><div class="footer-bottom"><span>© 2026 ColdDirect. Commercial refrigeration services.</span><span>Private website review</span></div></div></footer>
 <div class="mobile-actions" aria-label="Quick contact"><a href="tel:+447983759320">Call an engineer</a><a href="/contact/">Enquire</a></div>'''

def intro(title,lead,eyebrow='Commercial refrigeration · London',crumb='Services',actions=True):
 return f'''<section class="page-intro"><div class="wrap"><p class="breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span>{crumb}</p><p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p class="lead">{lead}</p>'''+('''<div class="intro-actions"><a class="button" href="tel:+447983759320">Call an engineer</a><a class="button button-outline" href="/contact/">Prepare an enquiry</a></div>''' if actions else '')+'''</div></section>'''

def document(title,description,body,active='',legacy=False,route='/'):
 return f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(description,quote=True)}"><meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#0b2539"><link rel="canonical" href="https://www.colddirect.co.uk{route}"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:type" content="website"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/review.css"><script src="/assets/review.js" defer></script></head><body>{header(active)}<main id="main-content" tabindex="-1" class="{'legacy-content' if legacy else 'review-content'}">{body}</main>{footer()}</body></html>'''

def save(route,content):
 p=DIST/(route.strip('/')+'/index.html' if route!='/' else 'index.html')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
 if route!='/': (DIST/(route.strip('/')+'.html')).write_text(content)

home='''<section class="home-hero"><div class="wrap home-hero-grid"><div><p class="eyebrow">Commercial refrigeration specialists · London</p><h1>Keeping your<br>business <span>cool.</span></h1><p class="hero-description">Fridges, freezers, cold rooms and more. Reliable refrigeration repair and planned maintenance for London's kitchens, shops and hospitality businesses.</p><div class="hero-actions"><a class="button button-cyan" href="tel:+447983759320">Call an engineer <span aria-hidden="true">↗</span></a><a class="button button-outline" href="/services/">Find your service <span aria-hidden="true">→</span></a></div><p class="small-note">24/7 emergency support. Call to confirm attendance.</p></div><figure class="hero-photo"><img src="/images/commercial-refrigeration-kitchen-20261014.webp" alt="Illustrative stainless steel commercial fridge in a restaurant kitchen" width="1279" height="720" fetchpriority="high" decoding="async"><div class="photo-label"><strong>Built around your business.</strong>Commercial equipment. Clear advice. A practical next step.</div><figcaption>Illustrative equipment image</figcaption></figure></div></section>
 <div class="trust-strip"><div class="wrap trust-row"><div><strong>Commercial specialists</strong><span>Kitchens, retail &amp; hospitality</span></div><div><strong>Emergency &amp; planned visits</strong><span>Support around your operation</span></div><div><strong>Based in North London</strong><span>25-mile service radius</span></div><div><strong>Repair costs explained</strong><span>Quote before work starts</span></div></div></div>
 <section class="section"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">What we repair</p><h2>The right service.<br>For your equipment.</h2></div><p>From a single prep fridge to a walk-in cold room, find help for the refrigeration your business depends on.</p></div><div class="service-grid">'''+''.join(card(s) for s in SERVICES[:6])+'''</div><div class="section-bottom"><a class="button button-outline" href="/services/">Explore all refrigeration services <span aria-hidden="true">→</span></a></div></div></section>
 <section class="maintenance-section"><div class="wrap maintenance-panel"><div><p class="eyebrow">Planned maintenance</p><h2>A little attention.<br>Fewer surprises.</h2><p>Arrange servicing around your equipment and opening hours. We inspect operating condition and explain what needs attention, helping you plan repairs before a busy service.</p><a class="text-link" href="/commercial-refrigeration-servicing-london/">Discuss a maintenance visit <span aria-hidden="true">→</span></a></div><ul class="maintenance-list"><li><span aria-hidden="true">✓</span>Condenser condition and airflow</li><li><span aria-hidden="true">✓</span>Door seals, closures and fan operation</li><li><span aria-hidden="true">✓</span>Controls, defrost and temperature checks</li><li><span aria-hidden="true">✓</span>Scope agreed for your equipment</li></ul></div></section>
 <section class="section process-section"><div class="wrap"><p class="eyebrow">A straightforward process</p><h2>From first call to a clear plan.</h2><div class="process-grid"><div><span class="step-number">01 / Tell us what's happening</span><h3>Start with a conversation.</h3><p>Call with your postcode, equipment make and model, and the fault. For a temperature problem, tell us the current reading.</p></div><div><span class="step-number">02 / Confirm the visit</span><h3>Know what comes next.</h3><p>We'll check your location, discuss urgency and confirm availability. Share a photo of the data plate to help identify the equipment.</p></div><div><span class="step-number">03 / Diagnose and explain</span><h3>Make an informed decision.</h3><p>An engineer checks the equipment and explains the repair and costs before work starts. If parts are needed, we'll discuss the next step.</p></div></div></div></section>
 <section class="section"><div class="wrap coverage-split"><div><p class="eyebrow">Local engineers · London coverage</p><h2>North London roots.<br>London-wide support.</h2><p>Based in Enfield, we work within a 25-mile radius of North London, including London and nearby Hertfordshire and Essex towns.</p><p>Call with your postcode to confirm coverage and the earliest available visit. Attendance depends on location and the day's workload.</p><a class="text-link" href="/coverage/">Explore our coverage <span aria-hidden="true">→</span></a></div><div class="coverage-areas"><h3>Supporting businesses across</h3><div class="area-links"><a href="/cold-room-repair-enfield/">Enfield</a><a href="/cold-room-repair-barnet/">Barnet</a><a href="/commercial-refrigeration-repair-camden/">Camden</a><a href="/commercial-refrigeration-repair-islington/">Islington</a><a href="/cold-room-repair-finchley/">Finchley</a><a href="/coverage/">Hertfordshire &amp; Essex</a></div><p class="small-note">Restaurants · Pubs &amp; bars · Hotels<br>Convenience stores · Catering kitchens</p></div></div></section>
 <div class="brand-strip"><div class="wrap"><p>Independent repairs for leading commercial brands</p><div class="brand-names"><a href="/foster-fridge-repair-london/">Foster</a><a href="/williams-fridge-repair-london/">Williams</a><a href="/polar-fridge-repair-london/">Polar</a><a href="/hoshizaki-ice-machine-repair-london/">Hoshizaki</a><a href="/true-fridge-repair-london/">True</a></div></div></div>
 <section class="section faq-section"><div class="wrap faq-layout"><div><p class="eyebrow">Before you call</p><h2>A few useful answers.</h2><p>Have a different question? Talk to the team.</p><a class="text-link" href="/faqs/">All frequently asked questions <span aria-hidden="true">→</span></a></div><div class="faq-list"><details><summary>Do you repair domestic fridges and freezers?</summary><p>ColdDirect specialises in commercial refrigeration for businesses. Household appliance repairs are outside this service.</p></details><details><summary>Can you attend an emergency breakdown?</summary><p>We offer 24/7 emergency support. Call 07983 759320 with your location and fault so the team can confirm availability and attendance.</p></details><details><summary>What should I have ready when I call?</summary><p>Your postcode, equipment make and model, a description of the fault, and any temperature or error-code reading. A photo of the data plate is helpful.</p></details><details><summary>Can you arrange planned maintenance?</summary><p>Yes. We can discuss a one-off servicing visit or a maintenance arrangement for your equipment. The scope, frequency and costs are agreed before booking.</p></details></div></div></section>'''
save('/',document('Commercial Refrigeration Repair London | ColdDirect','Commercial fridge, freezer, cold room and ice machine repair across London. Emergency support and planned maintenance from ColdDirect in Enfield.',home))

services=intro('Find the service<br>your business needs.','Choose your equipment below. For an urgent breakdown, call the team to confirm availability.','Repair & maintenance · Commercial equipment','Services')+'''<section class="section"><div class="wrap"><div class="filter-tools"><div><label class="search-label" for="service-search">Find equipment or a service</label><input class="service-search" id="service-search" type="search" placeholder="Try fridge, cold room or ice machine…" aria-controls="service-results" autocomplete="off"></div><div class="filter-pills" role="group" aria-label="Filter services">'''+''.join(f'<button type="button" data-service-filter="{val}" aria-pressed="{str(val=="all").lower()}">{label}</button>' for val,label in [('all','All services'),('kitchen','Kitchen & retail'),('rooms','Cold rooms'),('specialist','Specialist cooling'),('maintenance','Maintenance')])+'''</div></div><p class="results-status" id="results-status" role="status" aria-live="polite">15 services found</p><div class="service-grid" id="service-results">'''+''.join(card(s) for s in SERVICES)+'''</div><div class="no-results" id="no-results" hidden><h3>No matching services</h3><p>Try a different term or choose “All services”. If you're unsure, <a href="/contact/">contact the team</a> with your equipment details.</p></div><div class="section-bottom"><a class="text-link" href="/brands/">Looking for a particular brand? Explore brand repair pages →</a></div></div></section>'''
save('/services/',document('Commercial Refrigeration Services London | ColdDirect','Find commercial fridge, freezer, cold room, ice machine and specialist cooling repair services in London, plus planned refrigeration maintenance.',services,'/services/',route='/services/'))

contact=intro("Let's talk about<br>your refrigeration.",'For an urgent breakdown, call us. For planned work, prepare an enquiry with your site and equipment details.','Repairs · Servicing · Planned maintenance','Contact',False)+'''<section class="section"><div class="wrap contact-layout"><div class="contact-details"><h2>Speak to the team.</h2><div class="contact-option"><h3>Emergency support · 24/7</h3><a href="tel:+447983759320">07983 759320</a><p>Call with your postcode and fault. Attendance is confirmed by the team.</p></div><div class="contact-option"><h3>London office</h3><a href="tel:+442039524822">020 3952 4822</a><p>Repairs, servicing and maintenance enquiries.</p></div><div class="contact-option"><h3>Freephone</h3><a href="tel:+448001123427">0800 112 3427</a></div><div class="contact-option"><h3>Email</h3><a href="mailto:info@colddirect.co.uk">info@colddirect.co.uk</a><p>Include a photo of the equipment data plate if available.</p></div><div class="contact-address"><strong>Based in Enfield</strong><p>27 Felixstowe Road<br>Enfield, London N9 0DX</p><a class="text-link" href="/coverage/">Check service coverage →</a></div></div><div class="enquiry-panel"><h2>Prepare an enquiry.</h2><p>Complete the details to create an editable email draft. Open it in your email app and send it when ready. For emergencies, please call.</p><form id="enquiry-form"><div class="form-grid"><div class="form-field"><label for="enquiry-name">Your name *</label><input id="enquiry-name" name="name" required maxlength="100" autocomplete="name"></div><div class="form-field"><label for="enquiry-business">Business name</label><input id="enquiry-business" name="business" maxlength="120" autocomplete="organization"></div><div class="form-field"><label for="enquiry-phone">Phone number *</label><input id="enquiry-phone" name="phone" type="tel" required maxlength="40" autocomplete="tel"></div><div class="form-field"><label for="enquiry-email">Email address *</label><input id="enquiry-email" name="email" type="email" required maxlength="150" autocomplete="email"></div><div class="form-field"><label for="enquiry-postcode">Site postcode *</label><input id="enquiry-postcode" name="postcode" required maxlength="12" autocomplete="postal-code"></div><div class="form-field"><label for="enquiry-service">What do you need? *</label><select id="enquiry-service" name="service" required><option value="">Select a service</option>'''+''.join(f'<option>{escape(s[0])}</option>' for s in SERVICES)+'''<option>Other commercial refrigeration</option></select></div><div class="form-field full"><label for="enquiry-message">Equipment and fault *</label><textarea id="enquiry-message" name="message" required maxlength="1500" placeholder="Equipment make and model, fault or error code, current temperature, and preferred visit time…"></textarea></div></div><p class="form-note">These details stay in this page until you choose to send the email. Creating a draft does not confirm a booking.</p><button class="button" type="submit">Create email draft <span aria-hidden="true">→</span></button><p class="form-status" id="form-status" role="status" aria-live="polite"></p><noscript><p>You can <a href="mailto:info@colddirect.co.uk">email info@colddirect.co.uk</a> directly or call 07983 759320.</p></noscript></form><div class="draft-result" id="draft-result" hidden><h3 id="draft-heading" tabindex="-1">Your enquiry draft</h3><p>Check the details below. Nothing has been sent. You can edit the draft in your email app before sending.</p><label class="search-label" for="draft-text">Email text</label><textarea id="draft-text" readonly></textarea><div class="draft-actions"><a class="button" id="email-draft-link" href="mailto:info@colddirect.co.uk">Open email app</a><button class="button button-outline" type="button" id="copy-draft">Copy draft</button></div><p class="form-status" id="copy-status" role="status"></p></div></div></div></section>'''
save('/contact/',document('Contact ColdDirect | Commercial Refrigeration London','Call ColdDirect for emergency commercial refrigeration repair or prepare an email enquiry for planned servicing across London and nearby areas.',contact,'/contact/',route='/contact/'))

def remove(el):
 parent=el.getparent()
 if parent is not None: parent.remove(el)

def transform(path,route):
 original=path.read_text(errors='replace')
 tree=html.document_fromstring(original)
 source_canonical=tree.xpath('//link[@rel="canonical"]/@href')
 structured_data=tree.xpath('//script[@type="application/ld+json"]/text()')
 title=tree.findtext('.//title') or 'ColdDirect | Commercial Refrigeration London'
 desc=tree.xpath('//meta[@name="description"]/@content')
 refresh=tree.xpath('//meta[translate(@http-equiv,"REFSH","refsh")="refresh"]/@content')
 body=tree.find('body')
 if body is None: return None
 for el in body.xpath('.//script | .//style | .//header | .//footer | .//comment()'): remove(el)
 for el in body.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," sticky-cta ") or contains(concat(" ",normalize-space(@class)," ")," cd-topbar ") or contains(concat(" ",normalize-space(@class)," ")," topbar ") or contains(concat(" ",normalize-space(@class)," ")," cta-band ") or contains(concat(" ",normalize-space(@class)," ")," booking-modal ") or contains(concat(" ",normalize-space(@class)," ")," booking-fab ") or contains(concat(" ",normalize-space(@class)," ")," skip ")]'):remove(el)
 for el in body.xpath('.//nav[not(@aria-label="Breadcrumb")]'):remove(el)
 for form in body.xpath('.//form'):
  replacement=html.fragment_fromstring('<div class="enquiry-alternative"><p>Tell us your site postcode, equipment make and model, and the fault.</p><a class="button" href="/contact/">Prepare an enquiry</a><p class="small-note">For an urgent repair, call 07983 759320.</p></div>')
  form.getparent().replace(form,replacement)
 for row in body.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," cta-row ")]'):
  row.clear();row.set('class','cta-row')
  row.append(html.fragment_fromstring('<a class="button" href="tel:+447983759320">Call 07983 759320</a>'))
  row.append(html.fragment_fromstring('<a class="button button-outline" href="/contact/">Prepare an enquiry</a>'))
 for a in body.xpath('.//a[@href]'):
  href=a.get('href');u=urlsplit(href)
  if u.hostname in ['www.colddirect.co.uk','colddirect.co.uk']:href=urlunsplit(('', '', u.path or '/',u.query,u.fragment))
  if href in ['contact.asp','/contact.asp','booking.asp','/booking.asp','/booking.php','/book.php'] or a.get('data-open-booking') is not None: href='/contact/'
  if urlsplit(href).path.endswith('.asp'):
   p='/' + urlsplit(href).path.lstrip('/')[:-4]
   if (SOURCE/(p.lstrip('/')+'.html')).exists():href=p+'/'
  aliases={'/bottle-cooler-repair':'/bottle-cooler-repair-london/','/display-fridge-repair':'/display-fridge-repair-london/','/walk-in-cold-room-repair-london':'/cold-room-repair-london/','/commercial-cold-room-repair-london':'/cold-room-repair-london/'}
  if href.rstrip('/') in aliases:href=aliases[href.rstrip('/')]
  a.set('href',href)
  for attr in ['onclick','data-open-booking']:a.attrib.pop(attr,None)
 for el in body.xpath('.//*[@onclick]'):el.attrib.pop('onclick',None)
 for el in body.xpath('.//*[@style and not(self::img)]'):el.attrib.pop('style',None)
 for img in body.xpath('.//img[@src]'):
  src=img.get('src')
  if 'colddirect.co.uk/' in src:src='/'+src.split('colddirect.co.uk/',1)[1]
  image_aliases={'/images/drinks-fridge.webp':'/images/bottle-cooler-repair.webp','/images/fridge-room-repair.webp':'/images/cold-room-repair-london.webp','/images/walk-in-chiller-room.webp':'/images/cold-room.webp'}
  if src in image_aliases:src=image_aliases[src]
  img.set('src',src)
  if not img.get('alt'):img.set('alt','Commercial refrigeration equipment')
  img.set('decoding','async')
 for oldmain in body.xpath('.//main'):
  oldmain.tag='div';oldmain.attrib.pop('id',None)
 hero=body.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," hero ")]')
 if hero:
  wraps=hero[0].xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," wrap ")]')
  if wraps:wraps[0].insert(0,html.fragment_fromstring('<p class="breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/services/">Services</a></p>'))
 contents=(body.text or '')+''.join(etree.tostring(ch,encoding='unicode',method='html') for ch in body)
 contents=re.sub(r'(?:2[–-]4 hour|2 to 4 hour|two to four hour)(?: emergency)? response', 'attendance confirmed when you call', contents, flags=re.I)
 contents=contents.replace('Book a Free Consultation','Discuss your refrigeration').replace('book a free consultation','prepare an enquiry').replace('using the form on this page or the floating button','on our contact page').replace('Each URL is unique. Do not treat this list as a substitute for the local page.','Select your area for local service information.').replace('Informational articles. Not copies of our repair service pages.','Practical equipment guides for commercial kitchens, hospitality and food retail.').replace('Use the form on this page or the floating <strong>Book a Consultation</strong> button.','Use our contact page to prepare an email enquiry, or call for an urgent repair.')
 if not body.xpath('.//h1'):
  if refresh:
   target=re.split(r'url\s*=\s*',refresh[0],flags=re.I)[-1].strip(' "\'')
   u=urlsplit(target)
   if u.hostname in ['www.colddirect.co.uk','colddirect.co.uk']:target=u.path or '/'
   contents=intro('Find your refrigeration service.','Choose a service or continue to the page you were looking for.',actions=False)+f'<section class="section"><div class="wrap"><a class="button" href="{escape(target,quote=True)}">Continue to service →</a></div></section>'
  else:return None
 active='/services/' if ('repair' in route or 'cold-storage' in route or 'blast' in route) else route if route in ['/coverage/','/about-us/','/commercial-refrigeration-servicing-london/'] else ''
 result=document(title,desc[0] if desc else 'Commercial refrigeration repair and servicing across London from ColdDirect.',contents,active,True,route)
 if source_canonical and urlsplit(source_canonical[0]).hostname in ['www.colddirect.co.uk','colddirect.co.uk']:
  result=re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="'+escape(source_canonical[0],quote=True)+'">', result)
 for raw in structured_data:
  try: json.loads(raw)
  except ValueError: continue
  result=result.replace('</head>','<script type="application/ld+json">'+raw+'</script></head>')
 return result

exclude=['_backup','agent-status','gsc-','preview-']
paths={p.name:p for p in SOURCE.glob('*.html') if not any(p.name.startswith(x) for x in exclude)}
for directory in SOURCE.iterdir():
 if directory.is_dir() and (directory/'index.html').is_file() and directory.name not in ['colddirect-public-html','public','app','agent','mnt','preview-colddirect-homepage','agent-status']:
  paths[directory.name+'/index.html']=directory/'index.html'
for p in (SOURCE/'blog').rglob('*.html'): paths[str(p.relative_to(SOURCE))]=p

for name,path in paths.items():
 route='/' + (name[:-11] if name.endswith('/index.html') else name[:-5]).strip('/')+'/'
 if route in ['/index/','/services/','/contact/']:continue
 result=transform(path,route)
 if result:
  destination=DIST/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(result)
  # Make directory routes work for legacy .html files without Apache rewrites.
  if not name.endswith('/index.html'):
   routepath=DIST/(name[:-5]+'/index.html')
   if name[:-5]+'/index.html' not in paths:routepath.parent.mkdir(parents=True,exist_ok=True);routepath.write_text(result)

(DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
(DIST/'404.html').write_text(document('Page not found | ColdDirect','Find ColdDirect commercial refrigeration services.',intro('Let\'s find the right page.','This page could not be found. Explore our services or contact the team.','ColdDirect','Page not found',False)+'<section class="section"><div class="wrap"><a class="button" href="/services/">Explore services</a></div></section>'))

faq_items=[
 ('What equipment do you repair?','Commercial fridges and freezers, cold rooms, ice machines, display cabinets, cellar coolers, bottle coolers and specialist cooling equipment. <a href="/services/">Find your equipment in our service directory</a>.'),
 ('Do you offer emergency attendance?','ColdDirect offers 24/7 emergency support. Call 07983 759320 with your postcode, equipment and fault. The team will confirm availability and attendance; response times depend on location and workload.'),
 ('Do you repair domestic appliances?','This service is for commercial equipment in restaurants, pubs, hotels, shops and catering businesses. Household fridge and freezer repairs are outside the service.'),
 ('How much will a repair cost?','The cost depends on the equipment, diagnosis, parts and timing. Ask the team about call-out and diagnostic charges when arranging a visit. The engineer explains the proposed repair and costs before starting work.'),
 ('Which areas do you cover?','We are based in Enfield and work within a 25-mile radius of North London, including London and nearby Hertfordshire and Essex towns. Call with your postcode to confirm availability. <a href="/coverage/">See our coverage information</a>.'),
 ('What information helps when I contact you?','Your name and contact number, site postcode, equipment make and model, a description of the fault, and any temperature or error-code reading. A photo of the data plate helps identify parts and equipment.'),
 ('Can you service several units at one site?','Tell us the types, makes and number of units at your business so we can discuss the scope of a visit. If there are multiple faults, mention them when you arrange attendance.'),
 ('Do you offer planned maintenance?','Yes. We can discuss a one-off servicing visit or a maintenance arrangement for your equipment. Checks, timing and costs are agreed for your site. <a href="/commercial-refrigeration-servicing-london/">Read about planned maintenance</a>.'),
 ('What if the repair needs a replacement part?','The engineer explains what is needed and discusses the next step. Some parts may require ordering and a return visit. Ask about likely availability and costs before agreeing to the repair.'),
 ('Does the enquiry form confirm a booking?','The form prepares an editable email draft. You must send it through your email application. A booking is confirmed only after the team has agreed attendance with you. For urgent breakdowns, call rather than emailing.'),
]
faqs=intro('Useful answers.<br>Before you call.','Straightforward information about commercial repairs, coverage, costs and maintenance.','Commercial refrigeration · FAQs','FAQs',False)+'<section class="section"><div class="wrap faq-layout"><div><h2>Have another question?</h2><p>Talk to the team about your equipment and site.</p><a class="button" href="tel:+447983759320">Call 07983 759320</a></div><div class="faq-list">'+''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faq_items)+'</div></div></section>'
save('/faqs/',document('Commercial Refrigeration FAQs | ColdDirect London','Answers about ColdDirect commercial refrigeration repair, emergency attendance, maintenance, coverage and enquiry requests.',faqs,route='/faqs/'))
about=intro('Focused on the cooling<br>your business relies on.','ColdDirect provides commercial refrigeration repair and planned maintenance from its Enfield base, serving businesses across London and nearby areas.','Commercial refrigeration engineers · North London','About ColdDirect',False)+'''<section class="section"><div class="wrap coverage-split"><div><h2>Practical support.<br>For working businesses.</h2><p>We work with restaurants, pubs, bars, hotels, catering kitchens and food retailers. From prep fridges and upright freezers to walk-in rooms and ice machines, our work is centred on commercial equipment.</p><p>A breakdown and a planned servicing visit need different approaches. Tell us what is happening at your site so we can discuss the right next step, confirm availability and explain the proposed work.</p><p>We diagnose equipment and quote for the repair before starting. If a part needs ordering, we discuss the next step with you.</p><a class="text-link" href="/services/">Explore our services →</a></div><figure class="hero-photo"><img src="/images/fridge/commercial-fridge-kitchen-london.webp" alt="Illustrative commercial refrigeration equipment in a catering kitchen" width="1000" height="562" loading="lazy"><figcaption>Illustrative equipment image</figcaption></figure></div></section><section class="maintenance-section"><div class="wrap maintenance-panel"><div><p class="eyebrow">From Enfield, across London</p><h2>A local team.<br>A clear point of contact.</h2><p>27 Felixstowe Road, Enfield, London N9 0DX. Service coverage is within a 25-mile radius of North London. Call with your postcode to confirm attendance.</p><a class="text-link" href="/coverage/">View service coverage →</a></div><div><h3>Talk to ColdDirect</h3><p><a href="tel:+447983759320">07983 759320 · Emergency support</a><br><a href="tel:+442039524822">020 3952 4822 · London office</a><br><a href="mailto:info@colddirect.co.uk">info@colddirect.co.uk</a></p><a class="button" href="/contact/">Prepare an enquiry</a></div></div></section>'''
save('/about-us/',document('About ColdDirect | Commercial Refrigeration Engineers London','Enfield-based commercial refrigeration repair and planned maintenance for London restaurants, hospitality and food retail.',about,'/about-us/',route='/about-us/'))
print(json.dumps({'html_pages':len(list(DIST.rglob('*.html'))),'assets':len(list((DIST/'images').rglob('*')))}))

# Preserve access to the real booking flow; the static review never submits test bookings.
booking = '<div class="booking-preserved"><h2>Request a booking</h2><p>Use the existing ColdDirect booking form to send a real request. This opens the live website.</p><a class="button" href="https://www.colddirect.co.uk/contact/" target="_blank" rel="noopener">Open existing booking form</a></div>'
for page in DIST.rglob('*.html'):
 text=page.read_text()
 text=text.replace('<a href="/contact/">Prepare an enquiry →</a>', '<a href="https://www.colddirect.co.uk/contact/" target="_blank" rel="noopener">Existing booking form ↗</a>')
 if page == DIST/'contact/index.html': text=text.replace('<div class="enquiry-panel">','<div class="enquiry-panel">'+booking)
 page.write_text(text)
for slug in ['contact','services','about-us','faqs']:
 if (DIST/(slug+'.html')).exists(): shutil.copy2(DIST/slug/'index.html',DIST/(slug+'.html'))
