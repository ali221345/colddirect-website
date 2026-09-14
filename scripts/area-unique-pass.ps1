$ErrorActionPreference = 'Stop'
$root = 'C:\Users\khora\Documents\colddirect-website'
$pub = Join-Path $root 'colddirect-public-html'

$areas = @(
  @{ File='cold-room-repair-enfield.html'; Name='Enfield'; Neighbour='Edmonton'; Landmarks=@('Enfield Town','Church Street','Southbury Road'); Map='Enfield, London'; Mins='60 to 90'; Road='the A10 and Great Cambridge Road'; Sites='Church Street cafes, Palace Gardens kitchens and EN3 trading-estate pack rooms' }
  @{ File='cold-room-repair-barnet.html'; Name='Barnet'; Neighbour='New Barnet'; Landmarks=@('High Barnet','Barnet High Street','New Barnet'); Map='Barnet, London'; Mins='60 to 90'; Road='the A1000 and Barnet Hill'; Sites='High Street restaurants, Spires-area shops and hospital catering kitchens' }
  @{ File='cold-room-repair-edgware.html'; Name='Edgware'; Neighbour='Burnt Oak'; Landmarks=@('Station Road','The Broadwalk','Canons Park'); Map='Edgware, London'; Mins='60 to 90'; Road='the A5 and Edgware Way'; Sites='Station Road takeaways, Broadwalk back rooms and Canons Park hotels' }
  @{ File='cold-room-repair-finchley.html'; Name='Finchley'; Neighbour='Church End'; Landmarks=@('Finchley Central','Ballards Lane','Church End'); Map='Finchley, London'; Mins='50 to 80'; Road='the A406 and Ballards Lane'; Sites='Ballards Lane restaurants, Church End pubs and North Finchley shops' }
  @{ File='cold-room-repair-harrow.html'; Name='Harrow'; Neighbour='Wealdstone'; Landmarks=@('Harrow-on-the-Hill','Station Road','Wealdstone'); Map='Harrow, London'; Mins='60 to 90'; Road='the A404 and Station Road'; Sites='Hill restaurants, Station Road takeaways and Wealdstone cash-and-carry rooms' }
  @{ File='cold-room-repair-palmers-green.html'; Name='Palmers Green'; Neighbour='Winchmore Hill'; Landmarks=@('Green Lanes','Palmers Green station','Aldermans Hill'); Map='Palmers Green, London'; Mins='45 to 75'; Road='Green Lanes'; Sites='Green Lanes restaurants, Aldermans Hill cafes and Triangle shops' }
  @{ File='cold-room-repair-southgate.html'; Name='Southgate'; Neighbour='Cockfosters'; Landmarks=@('Southgate tube','The Bourne','Chase Side'); Map='Southgate, London'; Mins='45 to 75'; Road='the A111 and Chase Side'; Sites='The Bourne restaurants, Chase Side pubs and tube-parade kitchens' }
  @{ File='cold-room-repair-tottenham.html'; Name='Tottenham'; Neighbour='Seven Sisters'; Landmarks=@('Tottenham High Road','White Hart Lane','Seven Sisters'); Map='Tottenham, London'; Mins='40 to 70'; Road='the A10 High Road'; Sites='High Road takeaways, stadium-day kitchens and Seven Sisters shops' }
  @{ File='cold-room-repair-wembley.html'; Name='Wembley'; Neighbour='Wembley Park'; Landmarks=@('Wembley Park','Olympic Way','Wembley High Road'); Map='Wembley, London'; Mins='50 to 80'; Road='the A404 and Olympic Way'; Sites='High Road restaurants, Park hotels and event-day catering rooms' }
  @{ File='cold-room-repair-wood-green.html'; Name='Wood Green'; Neighbour='Turnpike Lane'; Landmarks=@('Wood Green High Road','Shopping City','Turnpike Lane'); Map='Wood Green, London'; Mins='40 to 70'; Road='the High Road and Turnpike Lane'; Sites='Shopping City back-of-house, High Road kitchens and Turnpike Lane takeaways' }
  @{ File='commercial-refrigeration-repair-camden.html'; Name='Camden'; Neighbour='Kentish Town'; Landmarks=@('Camden High Street','Camden Market','Kentish Town'); Map='Camden Town, London'; Mins='40 to 70'; Road='Camden High Street and the canal'; Sites='Market kitchens, High Street pubs and Primrose Hill restaurants' }
  @{ File='commercial-refrigeration-repair-islington.html'; Name='Islington'; Neighbour='Highbury'; Landmarks=@('Upper Street','Angel','Highbury'); Map='Islington, London'; Mins='40 to 70'; Road='Upper Street and the A1'; Sites='Angel restaurants, Upper Street pubs and Highbury takeaways' }
  @{ File='commercial-refrigeration-repair-hackney.html'; Name='Hackney'; Neighbour='Dalston'; Landmarks=@('Mare Street','Broadway Market','Dalston'); Map='Hackney, London'; Mins='45 to 75'; Road='Mare Street and the A10'; Sites='Broadway Market kitchens, Dalston bars and Mare Street shops' }
  @{ File='commercial-refrigeration-repair-haringey.html'; Name='Haringey'; Neighbour='Crouch End'; Landmarks=@('Wood Green','Tottenham High Road','Crouch End Broadway'); Map='Haringey, London'; Mins='40 to 70'; Road='the A105 and High Road'; Sites='Crouch End restaurants, Wood Green shops and Tottenham takeaways' }
  @{ File='commercial-refrigeration-repair-westminster.html'; Name='Westminster'; Neighbour='Victoria'; Landmarks=@('Oxford Street','Soho','Victoria'); Map='Westminster, London'; Mins='45 to 80'; Road='Oxford Street and Victoria Street'; Sites='Soho restaurants, hotel kitchens and Victoria catering rooms' }
  @{ File='commercial-refrigeration-repair-city-of-london.html'; Name='the City of London'; Neighbour='Smithfield'; Landmarks=@('Bank','Cheapside','Smithfield'); Map='City of London'; Mins='45 to 80'; Road='Cheapside and London Wall'; Sites='Cheapside restaurants, Bank kitchens and Smithfield meat rooms' }
  @{ File='commercial-refrigeration-repair-chelsea.html'; Name='Chelsea'; Neighbour='Fulham'; Landmarks=@("King's Road",'Sloane Square','Chelsea Harbour'); Map='Chelsea, London'; Mins='50 to 85'; Road="King's Road"; Sites="King's Road restaurants, Sloane Square hotels and Harbour kitchens" }
  @{ File='commercial-refrigeration-repair-kensington.html'; Name='Kensington'; Neighbour='Notting Hill'; Landmarks=@('Kensington High Street','Notting Hill Gate','Holland Park'); Map='Kensington, London'; Mins='50 to 85'; Road='Kensington High Street'; Sites='High Street restaurants, Notting Hill cafes and hotel walk-ins' }
  @{ File='commercial-refrigeration-repair-hammersmith.html'; Name='Hammersmith'; Neighbour='Shepherd''s Bush'; Landmarks=@('King Street','Hammersmith Broadway','the riverside'); Map='Hammersmith, London'; Mins='50 to 85'; Road='King Street and the A4'; Sites='Broadway restaurants, King Street pubs and riverside hotels' }
  @{ File='commercial-refrigeration-repair-southwark.html'; Name='Southwark'; Neighbour='London Bridge'; Landmarks=@('Borough Market','London Bridge','Bankside'); Map='Southwark, London'; Mins='50 to 85'; Road='Borough High Street'; Sites='Borough Market traders, Bankside restaurants and London Bridge hotels' }
  @{ File='commercial-refrigeration-repair-lambeth.html'; Name='Lambeth'; Neighbour='Brixton'; Landmarks=@('Brixton','Waterloo','Clapham'); Map='Lambeth, London'; Mins='50 to 85'; Road='Brixton Road and Waterloo'; Sites='Brixton Market kitchens, Waterloo restaurants and Clapham pubs' }
  @{ File='commercial-refrigeration-repair-wandsworth.html'; Name='Wandsworth'; Neighbour='Battersea'; Landmarks=@('Clapham Junction','Wandsworth Town','Battersea'); Map='Wandsworth, London'; Mins='55 to 90'; Road='the A3 and York Road'; Sites='Junction restaurants, Town pubs and Battersea kitchens' }
  @{ File='commercial-refrigeration-repair-tower-hamlets.html'; Name='Tower Hamlets'; Neighbour='Whitechapel'; Landmarks=@('Whitechapel','Canary Wharf','Brick Lane'); Map='Tower Hamlets, London'; Mins='50 to 85'; Road='Whitechapel Road and the Isle of Dogs'; Sites='Brick Lane kitchens, Wharf hotels and Whitechapel takeaways' }
  @{ File='commercial-refrigeration-repair-greenwich.html'; Name='Greenwich'; Neighbour='Deptford'; Landmarks=@('Greenwich Market','Cutty Sark','Deptford High Street'); Map='Greenwich, London'; Mins='55 to 95'; Road='the A2 and Creek Road'; Sites='Market kitchens, riverside restaurants and Deptford takeaways' }
  @{ File='commercial-refrigeration-repair-brent.html'; Name='Brent'; Neighbour='Kilburn'; Landmarks=@('Wembley','Kilburn High Road','Willesden'); Map='Brent, London'; Mins='45 to 80'; Road='the A5 and Wembley High Road'; Sites='Kilburn restaurants, Willesden shops and Wembley hotels' }
  @{ File='commercial-refrigeration-repair-ealing.html'; Name='Ealing'; Neighbour='West Ealing'; Landmarks=@('Ealing Broadway','West Ealing','South Ealing'); Map='Ealing, London'; Mins='50 to 85'; Road='the Uxbridge Road'; Sites='Broadway restaurants, West Ealing takeaways and hotel walk-ins' }
  @{ File='commercial-refrigeration-repair-richmond.html'; Name='Richmond'; Neighbour='Kew'; Landmarks=@('Richmond Hill','Richmond station','Kew'); Map='Richmond, London'; Mins='55 to 95'; Road='the A316 and Kew Road'; Sites='Hill restaurants, station-parade shops and Kew hotel kitchens' }
  @{ File='commercial-refrigeration-repair-croydon.html'; Name='Croydon'; Neighbour='South Croydon'; Landmarks=@('North End','East Croydon','Surrey Street'); Map='Croydon, London'; Mins='60 to 100'; Road='the A23 and Wellesley Road'; Sites='North End kitchens, East Croydon hotels and Surrey Street traders' }
  @{ File='commercial-refrigeration-repair-newham.html'; Name='Newham'; Neighbour='East Ham'; Landmarks=@('Stratford','Westfield Stratford','East Ham'); Map='Newham, London'; Mins='50 to 85'; Road='the A118 and Stratford High Street'; Sites='Westfield back-of-house, Stratford restaurants and East Ham takeaways' }
  @{ File='commercial-refrigeration-repair-hounslow.html'; Name='Hounslow'; Neighbour='Hounslow West'; Landmarks=@('Hounslow High Street','Hounslow West','Treaty Centre'); Map='Hounslow, London'; Mins='55 to 95'; Road='the A4 and Staines Road'; Sites='High Street kitchens, Treaty Centre shops and airport-corridor hotels' }
)

function Get-FaqPair($a) {
  $n = $a.Name
  $l1=$a.Landmarks[0]; $l2=$a.Landmarks[1]; $l3=$a.Landmarks[2]
  @{
    q1 = "How fast can you get to $n`?"
    a1 = "We aim for $($a.Mins) minutes for emergency commercial refrigeration in $n, including evenings and Sundays. Give us the postcode near $l1 and the current temperature when you call 07983 759320."
    q2 = "Do you cover $($a.Neighbour) near $n`?"
    a2 = "Yes. $($a.Neighbour) sits on the same North London diary as $n. We cover that neighbour and the streets around $l2 and $l3 on the same 24/7 rota."
  }
}

function Get-Intro($a) {
  $n = $a.Name
  $l1=$a.Landmarks[0]; $l2=$a.Landmarks[1]; $l3=$a.Landmarks[2]
@"
Cold Direct attends commercial refrigeration plant in $n around $l1, $l2 and $l3. We are a North London commercial team, not a domestic network, so the van is packed for walk-in cold rooms, prep fridges, bottle coolers and cellar plant used by restaurants, pubs, hotels and shops. Sites we see most weeks include $($a.Sites). Typical attendance is $($a.Mins) minutes via $($a.Road), including nights and Sundays. Tell us the room or cabinet temperature, whether the fans are turning, and send a photo of the data plate if you can. We quote on site after we test the plant. If you run a second site in $($a.Neighbour), we can often cover both on the same night when the diary allows. Call 07983 759320, 0800 112 3427 or 0203 952 4822. This page is only for $n trade work, not a copy of another borough URL. Keep the three numbers on the duty board so night porters can reach the same diary that covers $l1 and $l2.
"@
}

function Get-Block($a) {
  $faq = Get-FaqPair $a
  $intro = Get-Intro $a
  $mapQ = [uri]::EscapeDataString($a.Map)
@"
<!-- cd-area-unique:start -->
<div class="area-local">
  <h2>Local commercial refrigeration in $($a.Name)</h2>
  <p>$intro</p>
  <iframe title="Map of $($a.Name)" src="https://maps.google.com/maps?q=$mapQ&amp;output=embed" width="100%" height="280" style="border:0;margin:16px 0" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
  <h2>FAQs for $($a.Name)</h2>
  <h3>$($faq.q1)</h3>
  <p>$($faq.a1)</p>
  <h3>$($faq.q2)</h3>
  <p>$($faq.a2)</p>
</div>
<!-- cd-area-unique:end -->
"@
}

function Add-FaqSchema([string]$html, $a) {
  $faq = Get-FaqPair $a
  if ($html -match [regex]::Escape($faq.q1)) { return $html }
  $esc = { param($s) ($s -replace '\\','\\' -replace '"','\"') }
  $insert = @"
          {
            "@type": "Question",
            "name": "$(& $esc $faq.q1)",
            "acceptedAnswer": { "@type": "Answer", "text": "$(& $esc $faq.a1)" }
          },
          {
            "@type": "Question",
            "name": "$(& $esc $faq.q2)",
            "acceptedAnswer": { "@type": "Answer", "text": "$(& $esc $faq.a2)" }
          },
"@
  if ($html -match '"@type": "FAQPage"') {
    return [regex]::Replace($html, '("mainEntity":\s*\[)', "`$1`r`n$insert", 1)
  }
  return $html
}

function Resolve-File($name) {
  $r = Join-Path $root $name
  $p = Join-Path $pub $name
  if (Test-Path $r) { return $r }
  if (Test-Path $p) { return $p }
  return $null
}

$updated = 0
foreach ($a in $areas) {
  $path = Resolve-File $a.File
  if (-not $path) { Write-Output "MISSING $($a.File)"; continue }
  $html = [IO.File]::ReadAllText($path)
  $slug = [IO.Path]::GetFileNameWithoutExtension($a.File)
  $canon = "https://www.colddirect.co.uk/$slug"
  if ($html -match 'rel="canonical"') {
    $html = [regex]::Replace($html, '<link rel="canonical" href="[^"]*"\s*/?>', "<link rel=`"canonical`" href=`"$canon`">")
  } else {
    $html = $html -replace '</title>', "</title>`r`n  <link rel=`"canonical`" href=`"$canon`">"
  }
  $html = Add-FaqSchema $html $a
  $block = Get-Block $a
  if ($html -match 'cd-area-unique:start') {
    $html = [regex]::Replace($html, '(?s)<!-- cd-area-unique:start -->.*?<!-- cd-area-unique:end -->', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $block })
  } else {
    $html = [regex]::Replace($html, '(<section class="section">\s*<div class="wrap">)', "`$1`r`n$block", 1)
  }
  [IO.File]::WriteAllText($path, $html)
  $dst = if ($path.StartsWith($pub)) { Join-Path $root $a.File } else { Join-Path $pub $a.File }
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  Copy-Item $path $dst -Force
  $updated++
}
$hubItems = foreach ($a in $areas) {
  $slug = [IO.Path]::GetFileNameWithoutExtension($a.File)
  $label = if ($a.File -like 'cold-room-*') { "Cold room repair $($a.Name)" } else { "Commercial refrigeration repair $($a.Name)" }
  "        <li><a href=`"/$slug`">$label</a></li>"
}
$hubBlock = @"
<!-- cd-area-hub:start -->
<h2>Cold room and commercial refrigeration by area</h2>
<p>Use the dedicated area page for the town or borough. Each URL is unique. Do not treat this list as a substitute for the local page.</p>
<ul>
$($hubItems -join "`r`n")
</ul>
<!-- cd-area-hub:end -->
"@

function Add-Hub($fileName) {
  $path = Resolve-File $fileName
  if (-not $path) { Write-Output "HUB-MISSING $fileName"; return }
  $html = [IO.File]::ReadAllText($path)
  if ($html -match 'cd-area-hub:start') {
    $html = [regex]::Replace($html, '(?s)<!-- cd-area-hub:start -->.*?<!-- cd-area-hub:end -->', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $hubBlock })
  } else {
    $html = [regex]::Replace($html, '(<h2>We cover:</h2>)', "$hubBlock`r`n      `$1", 1)
    if ($html -notmatch 'cd-area-hub:start') {
      $html = [regex]::Replace($html, '(<section class="section">\s*<div class="wrap">)', "`$1`r`n$hubBlock", 1)
    }
  }
  [IO.File]::WriteAllText($path, $html)
  $dst = if ($path.ToLower().Contains('\colddirect-public-html\')) { Join-Path $root $fileName } else { Join-Path $pub $fileName }
  Copy-Item $path $dst -Force
  Write-Output "HUB=$fileName"
}

Add-Hub 'cold-room-repair-north-london.html'

$nl = Resolve-File 'cold-room-repair-north-london.html'
$londonHtml = [IO.File]::ReadAllText($nl)
$londonHtml = $londonHtml -replace '<title>[^<]+</title>', '<title>Cold Room Repair London | Areas We Cover | Cold Direct</title>'
$londonHtml = $londonHtml -replace '<link rel="canonical" href="[^"]*"\s*/?>', '<link rel="canonical" href="https://www.colddirect.co.uk/cold-room-repair-london">'
$londonHtml = $londonHtml -replace '<h1>[^<]+</h1>', '<h1>Cold Room Repair London</h1>'
$londonHtml = $londonHtml -replace 'Cold Room Repair North London', 'Cold Room Repair London'
$londonHtml = [regex]::Replace($londonHtml, '<meta name="description" content="[^"]*"', '<meta name="description" content="Cold room repair London by area. Unique pages for Enfield, Barnet, Camden and more. 24/7 commercial engineers. Call 07983 759320."')
[IO.File]::WriteAllText((Join-Path $root 'cold-room-repair-london.html'), $londonHtml)
[IO.File]::WriteAllText((Join-Path $pub 'cold-room-repair-london.html'), $londonHtml)
Add-Hub 'cold-room-repair-london.html'
Write-Output "UPDATED=$updated"
