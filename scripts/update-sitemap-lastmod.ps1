$root = 'C:\Users\khora\Documents\colddirect-website'
$public = Join-Path $root 'colddirect-public-html'
$sitemapPath = Join-Path $root 'sitemap.xml'
$xml = [IO.File]::ReadAllText($sitemapPath)

function Resolve-LocalFile([string]$loc) {
  $path = $loc -replace 'https://www\.colddirect\.co\.uk', ''
  $candidates = @()
  if ($path -eq '/' -or $path -eq '') {
    $candidates += (Join-Path $root 'index.html'), (Join-Path $public 'index.html')
  } elseif ($path.EndsWith('/')) {
    $rel = $path.TrimStart('/')
    $candidates += (Join-Path $root ($rel + 'index.html'))
    $candidates += (Join-Path $public ($rel + 'index.html'))
    $candidates += (Join-Path $root ($rel.TrimEnd('/') + '.html'))
    $candidates += (Join-Path $public ($rel.TrimEnd('/') + '.html'))
  } else {
    $rel = $path.TrimStart('/')
    $candidates += (Join-Path $root ($rel + '.html'))
    $candidates += (Join-Path $public ($rel + '.html'))
    $candidates += (Join-Path $root ($rel + '/index.html'))
    $candidates += (Join-Path $public ($rel + '/index.html'))
  }
  foreach ($c in $candidates) {
    if (Test-Path -LiteralPath $c) { return $c }
  }
  return $null
}

$xml = [regex]::Replace($xml, '(?s)(<loc>)([^<]+)(</loc>\s*<lastmod>)[^<]+(</lastmod>)', {
  param($m)
  $loc = $m.Groups[2].Value
  $file = Resolve-LocalFile $loc
  $date = if ($file) {
    (Get-Item -LiteralPath $file).LastWriteTimeUtc.ToString('yyyy-MM-dd')
  } else {
    (Get-Item -LiteralPath $sitemapPath).LastWriteTimeUtc.ToString('yyyy-MM-dd')
  }
  $m.Groups[1].Value + $loc + $m.Groups[3].Value + $date + $m.Groups[4].Value
})

[IO.File]::WriteAllText($sitemapPath, $xml)
Copy-Item $sitemapPath (Join-Path $public 'sitemap.xml') -Force
$locs = ([regex]::Matches($xml, '<loc>')).Count
$uniq = ([regex]::Matches($xml, '<lastmod>([^<]+)</lastmod>') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique) -join ','
Write-Output "LOCS=$locs DATES=$uniq"
