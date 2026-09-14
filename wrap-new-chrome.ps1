$ErrorActionPreference = "Stop"
$root = "C:\Users\khora\Documents\colddirect-website"

$header = @'
  <div class="topbar">Commercial Refrigeration London <strong>24/7</strong></div>
  <header class="site-header"><div class="wrap">
    <a class="no-underline" href="/"><span class="brand-cold">Cold</span><span class="brand-direct">Direct</span></a>
    <nav aria-label="Main navigation" class="site-nav">
      <details class="services-dropdown nav-item"><summary>Commercial Services <span class="nav-caret" aria-hidden="true">v</span></summary>
        <div class="services-dropdown-panel">
          <a href="/cold-room-repair-london.asp">Cold Room Repair London</a>
          <a href="/freezer-room-repair-london.asp">Freezer Room Repair London</a>
          <a href="/commercial-fridge-repair-london.asp">Commercial Fridge Repair London</a>
          <a href="/commercial-freezer-repair-london.asp">Commercial Freezer Repair London</a>
          <a href="/fridge-repair-london.asp">Fridge Repair London</a>
          <a href="/freezer-repair-london.asp">Freezer Repair London</a>
          <a href="/chiller-repair-london.asp">Chiller Repair London</a>
          <a href="/wine-cooler-repair-london.asp">Wine Cooler Repair London</a>
          <a href="/cellar-cooler-repair-london.asp">Cellar Cooler Repair London</a>
          <a href="/bottle-cooler-repair-london.asp">Bottle Cooler Repair London</a>
          <a href="/ice-machine-repair-london.asp">Ice Machine Repair London</a>
          <a href="/walk-in-fridge-repair-london.asp">Walk In Fridge Repair London</a>
          <a href="/walk-in-freezer-repair-london.asp">Walk In Freezer Repair London</a>
          <a href="/walk-in-cold-room-repair-london.asp">Walk In Cold Room Repair London</a>
        </div>
      </details>
      <a class="nav-link js-open-booking" href="#" data-open-booking role="button">Book a repair <span class="nav-arrow">-&gt;</span></a>
    </nav>
  </div></header>
'@

$footer = @'
  <footer class="site-footer"><div class="wrap">
    <div style="display:flex;flex-wrap:wrap;justify-content:space-between;gap:32px">
      <div><a href="/" class="text-2xl" style="font-size:1.5rem;font-weight:700;text-decoration:none">ColdDirect</a><p class="legal" style="border:0;margin:8px 0 0;padding:0">Commercial Refrigeration London 24/7</p></div>
      <nav aria-label="Footer" style="display:flex;flex-wrap:wrap;gap:20px;font-size:14px">
        <a href="/">Home</a>
        <a href="/about-us.html">About us</a>
        <a href="/contact.html">Contact</a>
        <a class="js-open-booking" href="#" data-open-booking role="button">Book a repair</a>
      </nav>
    </div>
    <p class="legal">© ColdDirect. All rights reserved.</p>
  </div></footer>
  <script>document.addEventListener('click',function(e){document.querySelectorAll('.services-dropdown[open]').forEach(function(d){if(!d.contains(e.target))d.open=false;});});</script>
  <script src="/js/booking.js?v=20260910d"></script>
</body>
</html>
'@

$keep = @(
  "about-us.html","contact.html",
  "cold-room-repair-barnet.html","cold-room-repair-edgware.html","cold-room-repair-enfield.html",
  "cold-room-repair-finchley.html","cold-room-repair-harrow.html","cold-room-repair-north-london.html",
  "cold-room-repair-palmers-green.html","cold-room-repair-southgate.html","cold-room-repair-tottenham.html",
  "cold-room-repair-wembley.html","cold-room-repair-wood-green.html",
  "commercial-dishwasher-repair-london.html",
  "commercial-freezer-repair-north-london.html","commercial-fridge-repair-north-london.html",
  "commercial-refrigeration-repair-brent.html","commercial-refrigeration-repair-camden.html",
  "commercial-refrigeration-repair-chelsea.html","commercial-refrigeration-repair-city-of-london.html",
  "commercial-refrigeration-repair-croydon.html","commercial-refrigeration-repair-ealing.html",
  "commercial-refrigeration-repair-greenwich.html","commercial-refrigeration-repair-hackney.html",
  "commercial-refrigeration-repair-hammersmith.html","commercial-refrigeration-repair-haringey.html",
  "commercial-refrigeration-repair-hounslow.html","commercial-refrigeration-repair-islington.html",
  "commercial-refrigeration-repair-kensington.html","commercial-refrigeration-repair-lambeth.html",
  "commercial-refrigeration-repair-newham.html","commercial-refrigeration-repair-richmond.html",
  "commercial-refrigeration-repair-southwark.html","commercial-refrigeration-repair-tower-hamlets.html",
  "commercial-refrigeration-repair-wandsworth.html","commercial-refrigeration-repair-westminster.html",
  "display-cabinet-repair-london.html","display-cabinet-repair-north-london.html",
  "freezer-room-repair-north-london.html",
  "hoshizaki-ice-machine-repair-london.html",
  "subzero-freezer-repair-london.html","williams-freezer-repair-london.html"
)

function Convert-Page($file) {
  $path = Join-Path $root $file
  if (-not (Test-Path $path)) { Write-Output "MISSING $file"; return }
  $html = Get-Content -Path $path -Raw -Encoding UTF8
  $title = "ColdDirect"
  if ($html -match '(?s)<title>(.*?)</title>') { $title = $Matches[1].Trim() }
  $desc = ""
  if ($html -match '(?s)<meta name="description" content="([^"]*)"') { $desc = $Matches[1] }
  $canonical = "https://www.colddirect.co.uk/" + ($file -replace '\.html$','')
  if ($html -match '(?s)<link rel="canonical" href="([^"]*)"') { $canonical = $Matches[1] }
  $schema = ""
  if ($html -match '(?s)(<script type="application/ld\+json"[^>]*>.*?</script>)') { $schema = $Matches[1] }

  $inner = $null
  if ($html -match '(?s)(<section class="hero">.*?)(?:<footer class="site-footer">|<div class="sticky-cta">)') {
    $inner = $Matches[1]
  } elseif ($html -match '(?s)</header>(.*?)(?:<footer class="site-footer">|<div class="sticky-cta">)') {
    $inner = $Matches[1]
  } else {
    Write-Output "NO INNER $file"
    return
  }
  $inner = $inner -replace '(?s)<script src="js/main.js"></script>', ''
  $inner = $inner -replace '(?s)<script src="js/booking.js"></script>', ''

  $head = @"
<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$title</title>
  <meta name="description" content="$desc">
  <link rel="canonical" href="$canonical">
  <link rel="stylesheet" href="css/cd-new.css?v=20260910a">
  $schema
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
$header
<main id="content">
$inner
</main>
$footer
"@
  [System.IO.File]::WriteAllText($path, $head, [System.Text.UTF8Encoding]::new($false))
  Write-Output "OK $file"
}

foreach ($f in $keep) { Convert-Page $f }
