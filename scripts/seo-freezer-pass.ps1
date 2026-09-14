$ErrorActionPreference = 'Stop'
$root = 'C:\Users\khora\Documents\colddirect-website'
$skipNames = @(
  'googlea72898072ed1602f.html'
)

function Test-ServicePage([string]$name) {
  return $name -match 'repair|fridge|freezer|cooler|cabinet|ice-|appliances|catering|polar|adexa|empire|williams|hoshizaki|subzero|cold-room'
}

function Convert-InternalHtmlLinks([string]$html) {
  $html = [regex]::Replace($html, 'https://www\.colddirect\.co\.uk/index\.html', 'https://www.colddirect.co.uk/')
  $html = [regex]::Replace($html, 'https://www\.colddirect\.co\.uk/([^"''\s]+)\.html', 'https://www.colddirect.co.uk/$1')
  $html = [regex]::Replace($html, 'href=(["''])/index\.html\1', 'href="/"')
  $html = [regex]::Replace($html, 'href=(["''])index\.html\1', 'href="/"')
  $html = [regex]::Replace($html, 'href=(["''])/([^"''#?]+)\.html([#?][^"'']*)?\1', {
    param($m)
    "href=`"/$($m.Groups[2].Value)$($m.Groups[3].Value)`""
  })
  $html = [regex]::Replace($html, 'href=(["''])(?!https?:|mailto:|tel:|#|/)([^"''#?]+\.html)([#?][^"'']*)?\1', {
    param($m)
    $path = $m.Groups[2].Value -replace '\.html$','' -replace '\\','/'
    $path = $path -replace '^\./',''
    while ($path.StartsWith('../')) { $path = $path.Substring(3) }
    "href=`"/$path$($m.Groups[3].Value)`""
  })
  return $html
}

function Set-Canonicals([string]$html, [string]$relUrl) {
  $canon = "https://www.colddirect.co.uk$relUrl"
  if ($html -match 'rel="canonical"') {
    $html = [regex]::Replace($html, '<link rel="canonical" href="[^"]*"\s*/?>', "<link rel=`"canonical`" href=`"$canon`">")
  } else {
    $html = $html -replace '</title>', "</title>`r`n  <link rel=`"canonical`" href=`"$canon`">"
  }
  $html = [regex]::Replace($html, 'property="og:url" content="[^"]*"', "property=`"og:url`" content=`"$canon`"")
  return $html
}

function Get-SchemaBlock([string]$serviceName) {
  $esc = $serviceName.Replace('\','\\').Replace('"','\"')
  return @"
  <script type="application/ld+json" data-cd-schema="local-service-faq">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "LocalBusiness",
        "name": "Cold Direct",
        "url": "https://www.colddirect.co.uk/",
        "telephone": "+447983759320",
        "areaServed": ["London", "Greater London"],
        "openingHoursSpecification": {
          "@type": "OpeningHoursSpecification",
          "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
          "opens": "00:00",
          "closes": "23:59"
        }
      },
      {
        "@type": "Service",
        "name": "$esc",
        "serviceType": "$esc",
        "provider": { "@type": "LocalBusiness", "name": "Cold Direct" },
        "areaServed": ["London", "Greater London"],
        "hoursAvailable": "Mo-Su 00:00-23:59"
      },
      {
        "@type": "FAQPage",
        "mainEntity": [
          {
            "@type": "Question",
            "name": "Do you offer 24/7 commercial refrigeration repair in London?",
            "acceptedAnswer": { "@type": "Answer", "text": "Yes. Cold Direct provides 24/7 emergency commercial refrigeration repair across London and Greater London, typically within 2 to 4 hours." }
          },
          {
            "@type": "Question",
            "name": "Which brands do you repair?",
            "acceptedAnswer": { "@type": "Answer", "text": "Foster, Williams, True, Polar, Blizzard, Gram, Hoshizaki and most other trade cabinets. Send a photo of the data plate." }
          },
          {
            "@type": "Question",
            "name": "Is Cold Direct commercial only?",
            "acceptedAnswer": { "@type": "Answer", "text": "Yes. We repair trade kitchens, shops and hotels. We do not take house fridge-freezers as a default." }
          },
          {
            "@type": "Question",
            "name": "How do I book commercial freezer repair london?",
            "acceptedAnswer": { "@type": "Answer", "text": "Call 07983 759320, 0800 112 3427 or 0203 952 4822. For cabinets use commercial freezer repair london on https://www.colddirect.co.uk/commercial-freezer-repair-london" }
          }
        ]
      }
    ]
  }
  </script>
"@
}

function Add-ServiceSchema([string]$html, [string]$serviceName) {
  if ($html -match 'data-cd-schema="local-service-faq"') { return $html }
  # Target page already has a full graph with FAQPage + Service
  if ($html -match '"@type": "Service"' -and $html -match '"@type": "FAQPage"') { return $html }
  $block = Get-SchemaBlock $serviceName
  if ($html -match '</head>') {
    return $html -replace '</head>', ($block + "</head>")
  }
  return $html + $block
}

function Update-ImageAlts([string]$html, [bool]$forceKw) {
  $html = [regex]::Replace($html, '<img\b([^>]*)>', {
    param($m)
    $tag = $m.Value
    $src = ''
    if ($tag -match 'src="([^"]+)"') { $src = $Matches[1] }
    $isLogo = $src -match 'logo|icon|favicon|badge'
    $hasAlt = $tag -match '\balt='
    $altVal = ''
    if ($tag -match 'alt="([^"]*)"') { $altVal = $Matches[1] }
    if ($isLogo) { return $tag }
    if (-not $hasAlt) {
      return $tag -replace '<img', '<img alt="commercial freezer repair london"'
    }
    if ($forceKw -and $altVal -notmatch 'commercial freezer repair london') {
      $newAlt = if ([string]::IsNullOrWhiteSpace($altVal)) { 'commercial freezer repair london' } else { "$altVal - commercial freezer repair london" }
      return [regex]::Replace($tag, 'alt="[^"]*"', "alt=`"$newAlt`"")
    }
    if ([string]::IsNullOrWhiteSpace($altVal)) {
      return [regex]::Replace($tag, 'alt="[^"]*"', 'alt="commercial freezer repair london"')
    }
    return $tag
  })
  return $html
}

function Get-RelUrl([System.IO.FileInfo]$file, [string]$base) {
  $rel = $file.FullName.Substring($base.Length).TrimStart('\','/').Replace('\','/')
  if ($rel -eq 'index.html') { return '/' }
  if ($rel -eq 'blog/index.html') { return '/blog/' }
  if ($rel -match '^blog/.+/index\.html$') { return '/' + ($rel -replace '/index\.html$','/') }
  if ($rel.EndsWith('.html')) { return '/' + $rel.Substring(0, $rel.Length - 5) }
  return '/' + $rel
}

$files = Get-ChildItem -Path $root -Filter *.html -Recurse -File | Where-Object {
  $_.FullName -notmatch '\\colddirect-public-html\\' -and
  $_.FullName -notmatch '\\node_modules\\' -and
  $skipNames -notcontains $_.Name
}

$changed = @()
foreach ($file in $files) {
  $html = [IO.File]::ReadAllText($file.FullName)
  $orig = $html
  $relUrl = Get-RelUrl $file $root
  $html = Convert-InternalHtmlLinks $html
  $html = Set-Canonicals $html $relUrl
  $isService = Test-ServicePage $file.Name
  if ($isService) {
    $title = if ($html -match '<title>(.*?)</title>') { $Matches[1] } else { 'Commercial refrigeration repair London' }
    $html = Add-ServiceSchema $html $title
  }
  $forceKw = $file.Name -match 'freezer' -or $file.FullName -match 'why-commercial-freezer'
  $html = Update-ImageAlts $html $forceKw
  if ($html -ne $orig) {
    [IO.File]::WriteAllText($file.FullName, $html)
    $changed += $file.FullName
  }
}

# Sitemap lastmod from file UTC write time; keep the same 61 locs
$sitemapPath = Join-Path $root 'sitemap.xml'
$sitemap = [IO.File]::ReadAllText($sitemapPath)
$sitemap = [regex]::Replace($sitemap, '(?s)<url>\s*<loc>([^<]+)</loc>\s*<lastmod>[^<]+</lastmod>', {
  param($m)
  $loc = $m.Groups[1].Value
  $path = $loc -replace 'https://www\.colddirect\.co\.uk',''
  $local = $null
  if ($path -eq '/' -or $path -eq '') { $local = Join-Path $root 'index.html' }
  elseif ($path.EndsWith('/')) {
    $try1 = Join-Path $root ($path.TrimStart('/') + 'index.html')
    $try2 = Join-Path $root ($path.TrimStart('/').TrimEnd('/') + '.html')
    if (Test-Path $try1) { $local = $try1 } elseif (Test-Path $try2) { $local = $try2 }
  } else {
    $try = Join-Path $root ($path.TrimStart('/') + '.html')
    if (Test-Path $try) { $local = $try }
  }
  $date = '2026-09-07'
  if ($local -and (Test-Path $local)) {
    $date = [datetime]::SpecifyKind((Get-Item $local).LastWriteTimeUtc, 'Utc').ToString('yyyy-MM-dd')
  }
  "<url>`r`n    <loc>$loc</loc>`r`n    <lastmod>$date</lastmod>"
})
[IO.File]::WriteAllText($sitemapPath, $sitemap)

# Mirror key files into colddirect-public-html
$public = Join-Path $root 'colddirect-public-html'
New-Item -ItemType Directory -Force -Path (Join-Path $public 'blog') | Out-Null
$mirror = @(
  'commercial-freezer-repair-london.html',
  'freezer-repair-london.html',
  'index.html',
  'sitemap.xml',
  'blog\why-commercial-freezer-not-freezing.html',
  'blog\index.html'
)
foreach ($rel in $mirror) {
  $src = Join-Path $root $rel
  $dst = Join-Path $public $rel
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  Copy-Item $src $dst -Force
}

# Apply same HTML transforms to remaining public-html pages (not sitemap)
$pubFiles = Get-ChildItem -Path $public -Filter *.html -Recurse -File | Where-Object { $skipNames -notcontains $_.Name }
foreach ($file in $pubFiles) {
  $html = [IO.File]::ReadAllText($file.FullName)
  $orig = $html
  $relUrl = Get-RelUrl $file $public
  $html = Convert-InternalHtmlLinks $html
  $html = Set-Canonicals $html $relUrl
  if (Test-ServicePage $file.Name) {
    $title = if ($html -match '<title>(.*?)</title>') { $Matches[1] } else { 'Commercial refrigeration repair London' }
    $html = Add-ServiceSchema $html $title
  }
  $forceKw = $file.Name -match 'freezer' -or $file.FullName -match 'why-commercial-freezer'
  $html = Update-ImageAlts $html $forceKw
  if ($html -ne $orig) {
    [IO.File]::WriteAllText($file.FullName, $html)
    $changed += $file.FullName
  }
}

Write-Output "CHANGED=$($changed.Count)"
Write-Output ($changed | Select-Object -First 80)
$locs = ([regex]::Matches((Get-Content $sitemapPath -Raw), '<loc>')).Count
Write-Output "SITEMAP_LOCS=$locs"
