$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$mirror = Join-Path $root "colddirect-public-html"

$nav = @(
  @{s="camden"; n="Camden"}, @{s="islington"; n="Islington"}, @{s="westminster"; n="Westminster"},
  @{s="city-of-london"; n="City"}, @{s="hackney"; n="Hackney"}, @{s="haringey"; n="Haringey"},
  @{s="kensington"; n="Kensington"}, @{s="chelsea"; n="Chelsea"}, @{s="hammersmith"; n="Hammersmith"},
  @{s="southwark"; n="Southwark"}, @{s="lambeth"; n="Lambeth"}, @{s="wandsworth"; n="Wandsworth"},
  @{s="tower-hamlets"; n="Tower Hamlets"}, @{s="greenwich"; n="Greenwich"}, @{s="brent"; n="Brent"},
  @{s="ealing"; n="Ealing"}, @{s="richmond"; n="Richmond"}, @{s="croydon"; n="Croydon"},
  @{s="newham"; n="Newham"}, @{s="hounslow"; n="Hounslow"}
)

function Get-AreaLinks([string]$current) {
  ($nav | ForEach-Object {
    $href = "commercial-refrigeration-repair-$($_.s).html"
    if ($_.s -eq $current) { "<strong>$($_.n)</strong>" } else { "<a href=`"$href`">$($_.n)</a>" }
  }) -join " | "
}

$areas = @(
  @{ slug="camden"; name="Camden"; title="Commercial Refrigeration Repair Camden | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Camden. Cold rooms, market cabinets and cellar coolers. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Camden - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Camden"
    lead="Walk-in cold rooms, market cabinets, pub cellars and restaurant fridges across Camden Town, Kentish Town, Primrose Hill and Chalk Farm. Typical attendance 60 to 90 minutes. Call 0203 952 4822."
    postcodes="NW1, NW3, NW5 and NW6"
    places="Camden Town, Camden Market, Parkway, Camden High Street, Kentish Town, Chalk Farm, Primrose Hill, Gospel Oak, Swiss Cottage and Mornington Crescent"
    nearby="Islington, Westminster, Haringey and Brent"
    unique=@"
      <h2>Commercial refrigeration for Camden kitchens and market sites</h2>
      <p>Camden is one of the busiest hospitality boroughs in London. A Saturday at Camden Market, a late service on Parkway, or a Sunday roast in Primrose Hill all depend on plant that holds temperature. Cold Direct is a commercial-only refrigeration team covering Camden from North London. We repair walk-in cold rooms, freezer rooms, prep counters, glass display cabinets, bottle coolers, cellar coolers and ice machines. We do not take domestic house call-outs.</p>
      <p>Competitors who already rank for commercial refrigeration repair Camden talk about four-hour windows. We book the engineer on the phone and typically reach NW1 and NW5 sites in 60 to 90 minutes, including evenings and Sundays. Tell us the current air temperature, the make on the data plate, and whether the fans are still turning.</p>
      <p>Camden Market food traders run serve-over wells and under-counter fridges in cramped pitches with poor airflow. Condensers sit behind plywood, next to fryers, or under a stall where dust and grease cake the coil. We pull the unit, clean the condenser, check the door furniture, and tell you if the compressor is still worth saving.</p>
      <p>On Camden High Street and Parkway we see mixed Williams, Foster, Polar and Blizzard cabinets, plus older pack systems on the roof. Plant decks collect blossom, takeaway grease and pigeon debris. A tripped condensing unit takes the whole walk-in with it. Kentish Town pubs and music venues run cellar coolers through a late finish. Night work is standard. We will not ask staff to chip ice with a metal bar.</p>
      <p>Search for commercial refrigeration London plus Camden and you currently see dedicated area URLs from other engineers. A homepage that only lists Camden in a footer cannot beat that. This page exists so Cold Direct can compete on the same query with local copy, LocalBusiness markup, and a clear path to <a href="https://www.colddirect.co.uk/contact.html">contact</a>.</p>
"@ }
  @{ slug="islington"; name="Islington"; title="Commercial Refrigeration Repair Islington | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Islington. Upper Street, Angel and Clerkenwell. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Islington - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Islington"
    lead="Cold rooms, prep fridges and cellar plant for Upper Street, Angel, Clerkenwell and Highbury. Call 0203 952 4822."
    postcodes="N1, N7 and EC1 on the Clerkenwell boundary"
    places="Angel, Upper Street, Clerkenwell, Highbury, Canonbury, Barnsbury and King's Cross edge sites"
    nearby="Camden, City of London, Hackney and Haringey"
    unique=@"
      <h2>Commercial refrigeration along Upper Street and Angel</h2>
      <p>Islington packs more restaurant, pub and cafe refrigeration into a short stretch of N1 than most London boroughs. Upper Street, Exmouth Market and the lanes around Angel run long hours. When a walk-in climbs during Saturday brunch, the pass stops. Cold Direct covers Islington from our North London radius and books the engineer on the phone.</p>
      <p>Typical faults are dirty condensers in basement plant rooms, failed evaporator fans on Williams and Foster uprights, leaking door heaters on walk-ins, and cellar coolers that cannot keep up after a barrel delivery. Clerkenwell hotel kitchens often have remote packs on roofs. Highbury takeaways run older Polar and Blizzard under-counters. We tell you honestly if a repair is cheaper than a replacement.</p>
"@ }
  @{ slug="westminster"; name="Westminster"; title="Commercial Refrigeration Repair Westminster | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Westminster, Soho, Covent Garden and Victoria. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Westminster - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Westminster"
    lead="Soho, Covent Garden, Victoria and Mayfair hospitality plant. 24/7 commercial-only repair. Call 0203 952 4822."
    postcodes="W1, SW1 and WC2"
    places="Soho, Covent Garden, Chinatown, Mayfair, Marylebone, Victoria, Pimlico and the West End"
    nearby="Camden, City of London, Kensington and Chelsea"
    unique=@"
      <h2>West End commercial refrigeration that cannot wait until Monday</h2>
      <p>Westminster hospitality runs from breakfast in Marylebone to 2am in Soho. A failed walk-in behind a Covent Garden restaurant is a trading emergency. Access in W1 and WC2 is the job as much as the fault: Congestion Charge, loading bays, basement hatches and night restrictions. Tell us the nearest cross street and whether we need a night slot.</p>
      <p>Soho and Chinatown kitchens stack cabinets in rooms with almost no ventilation. Hotel groups around Victoria often need a written attendance note. Email info@colddirect.co.uk via <a href="https://www.colddirect.co.uk/contact.html">the contact page</a>. We still refuse domestic houses above the shop.</p>
"@ }
  @{ slug="city-of-london"; name="City of London"; title="Commercial Refrigeration Repair City of London | Cold Direct"
    meta="24/7 commercial refrigeration repair in the City of London. Office canteens, hotels and restaurants. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers City of London - 24/7"
    h1="Commercial Refrigeration Repair in the City of London"
    lead="Square Mile canteens, hotels and restaurants. Commercial plant only. Call 0203 952 4822."
    postcodes="EC1, EC2, EC3 and EC4"
    places="Bank, Liverpool Street, Barbican, Smithfield, Monument, Cannon Street and the Square Mile"
    nearby="Islington, Tower Hamlets, Westminster and Southwark"
    unique=@"
      <h2>City canteens and restaurant rooms that must hold through the week</h2>
      <p>The City is office restaurants, hotel kitchens, members' clubs and the remaining traders around Smithfield. When a canteen cold room fails on a Tuesday morning, hundreds of covers are at risk before lunch. Building management in EC2 and EC3 often wants a named engineer, a time window and a risk note. Call 0203 952 4822 for planned work. Use the mobile after hours.</p>
      <p>Weekend City sites are quieter on the street and harder on access. Many buildings shut loading after Friday. Tell us if we need Saturday attendance while security is on a reduced rota.</p>
"@ }
  @{ slug="hackney"; name="Hackney"; title="Commercial Refrigeration Repair Hackney | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Hackney, Shoreditch, Dalston and Broadway Market. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Hackney - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Hackney"
    lead="Shoreditch, Dalston, London Fields and Broadway Market kitchens. Call 0203 952 4822."
    postcodes="E8, E9, E2 and N16 on the Stoke Newington edge"
    places="Shoreditch, Dalston, London Fields, Broadway Market, Homerton, Hackney Central and Stoke Newington"
    nearby="Islington, Tower Hamlets, Haringey and the City"
    unique=@"
      <h2>Hackney restaurants, bakeries and market traders</h2>
      <p>Hackney's food scene is dense, independent and hard on refrigeration. Broadway Market kitchens, Dalston restaurants and Shoreditch late sites all run cabinets in small footprints. A bakery walk-in that warms overnight ruins the next day's production. Plant in converted warehouses is often a mix of monoblock cold rooms and cheap under-counters. We work on both.</p>
      <p>Stoke Newington delis and wine shops are in scope when the cabinet is commercial. House wine fridges are not.</p>
"@ }
  @{ slug="haringey"; name="Haringey"; title="Commercial Refrigeration Repair Haringey | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Haringey, Crouch End, Wood Green and Tottenham. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Haringey - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Haringey"
    lead="Crouch End, Muswell Hill, Wood Green and Tottenham commercial plant. Call 0203 952 4822."
    postcodes="N8, N10, N15, N17 and N22"
    places="Crouch End, Muswell Hill, Wood Green, Turnpike Lane, Tottenham, Seven Sisters and Hornsey"
    nearby="Camden, Islington, Enfield and Barnet"
    unique=@"
      <h2>Haringey is already on our North London run</h2>
      <p>Haringey is home ground. Wood Green, Tottenham and Palmers Green already have cold room pages. This borough page ties commercial refrigeration repair Haringey into one URL for people who search the council name. Crouch End and Muswell Hill restaurants expect a fast night call. Tottenham High Road kitchens run late with heavy door traffic.</p>
      <p>If you already used our <a href="cold-room-repair-wood-green.html">Wood Green</a> or <a href="cold-room-repair-tottenham.html">Tottenham</a> pages, this is the wider commercial refrigeration landing.</p>
"@ }
  @{ slug="kensington"; name="Kensington"; title="Commercial Refrigeration Repair Kensington | Cold Direct"
    meta="24/7 commercial refrigeration repair in Kensington and South Kensington hotels and restaurants. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Kensington - 24/7"
    h1="Commercial Refrigeration Repair in Kensington"
    lead="Hotels, restaurants and clubs in Kensington and South Kensington. Call 0203 952 4822."
    postcodes="W8, SW7 and W14 on the Holland Park edge"
    places="Kensington High Street, South Kensington, Holland Park, Earl's Court and Knightsbridge edge sites"
    nearby="Chelsea, Westminster, Hammersmith and Camden"
    unique=@"
      <h2>Hotel and restaurant plant in Kensington</h2>
      <p>Kensington hospitality is hotel-heavy. South Kensington kitchens and High Street Kensington restaurants need quiet, documented repairs. Basement cold rooms in W8 often share plant space with laundry heat. Condensers run hot. We look at airflow and the set point before we talk about a new pack. Museums and institutional catering on the Exhibition Road side are commercial sites.</p>
"@ }
  @{ slug="chelsea"; name="Chelsea"; title="Commercial Refrigeration Repair Chelsea | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair on the King's Road and Chelsea hotels. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Chelsea - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Chelsea"
    lead="King's Road, Sloane Square and Chelsea hotel kitchens. Call 0203 952 4822."
    postcodes="SW3, SW10 and SW1W on the Sloane Square edge"
    places="King's Road, Sloane Square, Chelsea Harbour, World's End and South Kensington edge"
    nearby="Kensington, Westminster, Wandsworth and Hammersmith"
    unique=@"
      <h2>Chelsea restaurants and hotel cold rooms</h2>
      <p>Chelsea kitchens are compact, expensive to take offline, and often in listed buildings. Parking and loading on SW3 need a clear arrival window. Tell us if we should come after service. Chelsea Harbour and World's End add pubs and cellar coolers on the same call-out as the walk-in.</p>
"@ }
  @{ slug="hammersmith"; name="Hammersmith"; title="Commercial Refrigeration Repair Hammersmith | Cold Direct"
    meta="24/7 commercial refrigeration repair in Hammersmith and Shepherd's Bush. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Hammersmith - 24/7"
    h1="Commercial Refrigeration Repair in Hammersmith"
    lead="King Street, Shepherd's Bush and riverside kitchens. Call 0203 952 4822."
    postcodes="W6, W12 and W14"
    places="Hammersmith Broadway, King Street, Shepherd's Bush, White City and Brook Green"
    nearby="Kensington, Chelsea, Ealing and Brent"
    unique=@"
      <h2>Hammersmith and Shepherd's Bush trade refrigeration</h2>
      <p>Hammersmith Broadway and King Street run pubs, hotels and restaurants with plant on roofs above the flyover. Shepherd's Bush and White City add shopping-centre food trade. Response from North London depends on the A40 and Westway. We will be honest if a job will be longer. Office canteens around the riverside need planned slots as well as breakdowns.</p>
"@ }
  @{ slug="southwark"; name="Southwark"; title="Commercial Refrigeration Repair Southwark | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Southwark, Borough Market and London Bridge. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Southwark - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Southwark"
    lead="Borough Market, London Bridge, Bermondsey and Bankside commercial plant. Call 0203 952 4822."
    postcodes="SE1, SE16 and SE15 on the Peckham edge"
    places="Borough Market, London Bridge, Bermondsey, Bankside, Elephant and Castle and Peckham"
    nearby="City of London, Lambeth, Tower Hamlets and Westminster"
    unique=@"
      <h2>Borough Market and London Bridge cold plant</h2>
      <p>Southwark's food trade is intense around Borough Market. Traders cannot lose a well or a walk-in on a Saturday. Market pitches have the same problems as Camden Market: grease on condensers, no airflow, and cabinets never sized for the heat of the neighbouring stall. Bermondsey railway arches hold production kitchens. Access can be a loading-bay conversation.</p>
"@ }
  @{ slug="lambeth"; name="Lambeth"; title="Commercial Refrigeration Repair Lambeth | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Lambeth, Brixton, Vauxhall and Waterloo. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Lambeth - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Lambeth"
    lead="Brixton, Vauxhall, Waterloo and Clapham edge kitchens. Call 0203 952 4822."
    postcodes="SW8, SW9, SW2, SE11 and SE1 on the Waterloo side"
    places="Brixton, Vauxhall, Waterloo, Kennington, Stockwell and Clapham edge"
    nearby="Southwark, Wandsworth, Westminster and Chelsea"
    unique=@"
      <h2>Brixton, Vauxhall and Waterloo commercial refrigeration</h2>
      <p>Lambeth runs from Waterloo hotels to Brixton Market and the Vauxhall riverside. Travel from North London is longer than a Camden job when the river crossings are slow. We still take the call and we still give a time. We do not promise a 20-minute miracle from Enfield to SW9. Waterloo and South Bank hotels want documented night work.</p>
"@ }
  @{ slug="wandsworth"; name="Wandsworth"; title="Commercial Refrigeration Repair Wandsworth | Cold Direct"
    meta="24/7 commercial refrigeration repair in Wandsworth, Clapham Junction and Battersea. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Wandsworth - 24/7"
    h1="Commercial Refrigeration Repair in Wandsworth"
    lead="Clapham Junction, Battersea, Tooting and Wandsworth Town. Call 0203 952 4822."
    postcodes="SW18, SW11, SW12 and SW17"
    places="Wandsworth Town, Clapham Junction, Battersea, Tooting and Balham"
    nearby="Lambeth, Chelsea, Richmond and Hammersmith"
    unique=@"
      <h2>South-west London hospitality plant</h2>
      <p>Wandsworth is a long borough of high streets and new riverside kitchens. New Battersea developments often have tight plant rooms. Older Tooting sites have cabinets that have never had a condenser clean. Pubs around Wandsworth Town still run cellar coolers. A warm cellar on a Friday is an emergency.</p>
"@ }
  @{ slug="tower-hamlets"; name="Tower Hamlets"; title="Commercial Refrigeration Repair Tower Hamlets | Cold Direct"
    meta="24/7 commercial refrigeration repair in Tower Hamlets, Brick Lane and Canary Wharf. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Tower Hamlets - 24/7"
    h1="Commercial Refrigeration Repair in Tower Hamlets"
    lead="Brick Lane, Whitechapel, Canary Wharf and Wapping kitchens. Call 0203 952 4822."
    postcodes="E1, E2, E3 and E14"
    places="Brick Lane, Whitechapel, Spitalfields, Canary Wharf, Poplar, Bow and Wapping"
    nearby="City of London, Hackney, Newham and Southwark"
    unique=@"
      <h2>East London kitchens from Brick Lane to Canary Wharf</h2>
      <p>Tower Hamlets splits into two refrigeration worlds. Brick Lane and Whitechapel run independent restaurants with hard-used cabinets. Canary Wharf runs contract catering and hotels with FM rules. Tell us which world you are in on the first call so we send the right expectation on time and paperwork. Canary Wharf night work is often easier than a weekday lunch slot.</p>
"@ }
  @{ slug="greenwich"; name="Greenwich"; title="Commercial Refrigeration Repair Greenwich | Cold Direct"
    meta="24/7 commercial refrigeration repair in Greenwich, Greenwich Market and Woolwich. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Greenwich - 24/7"
    h1="Commercial Refrigeration Repair in Greenwich"
    lead="Greenwich Market, the town centre and Woolwich hospitality plant. Call 0203 952 4822."
    postcodes="SE10, SE18 and SE3"
    places="Greenwich town centre, Greenwich Market, Greenwich Peninsula, Blackheath edge and Woolwich"
    nearby="Tower Hamlets, Southwark and Newham"
    unique=@"
      <h2>Greenwich Market and riverside hospitality</h2>
      <p>Greenwich Market traders and restaurants around the park run cabinets in tourist heat and tight pitches. A failed display on a bank holiday weekend is a lost trading day. Peninsula hotels and O2-side catering need building access arranged. Woolwich riverside kitchens add walk-ins in new-build plant rooms. Travel from North London is longer than an Islington job. We still take emergencies.</p>
"@ }
  @{ slug="brent"; name="Brent"; title="Commercial Refrigeration Repair Brent | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Brent, Wembley, Kilburn and Willesden. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Brent - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Brent"
    lead="Wembley, Kilburn, Willesden and Neasden commercial plant. Call 0203 952 4822."
    postcodes="NW10, NW2, NW6 and HA0"
    places="Wembley, Kilburn, Willesden, Neasden, Harlesden and Queens Park"
    nearby="Camden, Westminster, Harrow and Ealing"
    unique=@"
      <h2>Brent and Wembley commercial refrigeration</h2>
      <p>Brent already sits next to our existing <a href="cold-room-repair-wembley.html">Wembley cold room page</a>. This borough URL captures searches for commercial refrigeration repair Brent, Kilburn and Willesden. Wembley event days change access. Tell us if the stadium is on. Kilburn High Road restaurants and Willesden takeaways run late. Typical response 60 to 90 minutes.</p>
"@ }
  @{ slug="ealing"; name="Ealing"; title="Commercial Refrigeration Repair Ealing | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Ealing, Acton and Southall. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Ealing - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Ealing"
    lead="Ealing Broadway, Acton, Southall and Hanwell kitchens. Call 0203 952 4822."
    postcodes="W5, W3, W7 and W13"
    places="Ealing Broadway, West Ealing, Acton, Southall, Hanwell and Northfields"
    nearby="Hammersmith, Brent, Hounslow and Harrow"
    unique=@"
      <h2>Ealing Broadway and Southall trade refrigeration</h2>
      <p>Ealing mixes Broadway restaurants with Southall food production and Acton takeaways. Walk-in rooms behind Southall high-street kitchens work hard and fail when condensers are ignored. Southall production sites may have larger pack systems. Tell us horsepower and refrigerant if you know them. Restaurant cabinets on the Broadway are the same Williams, Foster and Polar work we do every day.</p>
"@ }
  @{ slug="richmond"; name="Richmond"; title="Commercial Refrigeration Repair Richmond | Cold Direct"
    meta="24/7 commercial refrigeration repair in Richmond, Twickenham and Kew. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Richmond - 24/7"
    h1="Commercial Refrigeration Repair in Richmond"
    lead="Richmond town, Twickenham and Kew hospitality plant. Call 0203 952 4822."
    postcodes="TW9, TW1 and TW10"
    places="Richmond town centre, The Green, Twickenham, Kew and East Sheen"
    nearby="Wandsworth, Hounslow and Hammersmith"
    unique=@"
      <h2>Richmond and Twickenham pubs, hotels and restaurants</h2>
      <p>Richmond's riverside pubs and Twickenham event days put serious load on cellar coolers and walk-ins. When a cellar climbs before a match Saturday, stock and trade go together. Travel from North London is a longer slot. Hotel kitchens near the Green and Kew restaurants often want a quiet morning visit. Book the office number for those. Night emergencies still use the mobile.</p>
"@ }
  @{ slug="croydon"; name="Croydon"; title="Commercial Refrigeration Repair Croydon | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Croydon town centre and South Croydon. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Croydon - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Croydon"
    lead="Croydon town centre, South Croydon and Purley edge kitchens. Call 0203 952 4822."
    postcodes="CR0, CR2 and CR7"
    places="Croydon town centre, South Croydon, Thornton Heath, Purley edge and Addiscombe"
    nearby="Lambeth, Wandsworth and Sutton edge"
    unique=@"
      <h2>Croydon town-centre and high-street refrigeration</h2>
      <p>Croydon is a large commercial centre south of the river. Competitors already treat it as a named service area. This page is the dedicated commercial refrigeration repair Croydon URL so the borough is not only a footer word. Town-centre restaurants, hotel kitchens and shop displays fail in the same ways as North London. Travel time is longer than Barnet. We will tell you if we can reach you the same night.</p>
"@ }
  @{ slug="newham"; name="Newham"; title="Commercial Refrigeration Repair Newham | 24/7 | Cold Direct"
    meta="24/7 commercial refrigeration repair in Newham, Stratford and East Ham. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Newham - 24/7 emergency"
    h1="Commercial Refrigeration Repair in Newham"
    lead="Stratford, East Ham, Forest Gate and Canning Town commercial plant. Call 0203 952 4822."
    postcodes="E13, E15, E6 and E16"
    places="Stratford, East Ham, Forest Gate, Canning Town, Plaistow and West Ham"
    nearby="Tower Hamlets, Hackney, Greenwich and Redbridge edge"
    unique=@"
      <h2>Stratford and East Ham commercial refrigeration</h2>
      <p>The homepage already names Stratford on the coverage ring. Newham is the borough wrapper for commercial refrigeration repair Stratford, East Ham and Canning Town. Westfield-side catering, hotel kitchens and Green Street restaurants all run trade plant. Stratford hotel work can need security sign-in. Independent restaurants on the high streets can use the mobile.</p>
"@ }
  @{ slug="hounslow"; name="Hounslow"; title="Commercial Refrigeration Repair Hounslow | Cold Direct"
    meta="24/7 commercial refrigeration repair in Hounslow, Chiswick and Heathrow-edge hotels. Call 0203 952 4822."
    kicker="Commercial refrigeration engineers Hounslow - 24/7"
    h1="Commercial Refrigeration Repair in Hounslow"
    lead="Hounslow High Street, Chiswick, Brentford and airport-edge hotels. Call 0203 952 4822."
    postcodes="TW3, W4, TW8 and TW6 edge"
    places="Hounslow High Street, Chiswick, Brentford, Isleworth and Heathrow-edge hotels"
    nearby="Ealing, Richmond and Hammersmith"
    unique=@"
      <h2>Hounslow, Chiswick and airport-edge hotel plant</h2>
      <p>Hounslow High Street restaurants, Chiswick hospitality and Heathrow-edge hotels need commercial refrigeration that holds through long days. Airport hotels often need out-of-hours windows and a named contact. Chiswick and Brentford riverside kitchens sit closer to Hammersmith than to Enfield. We will give a realistic arrival. We will not invent a 20-minute SLA.</p>
"@ }
)

function Get-SharedBody($a) {
  $n = $a.name
  $pc = $a.postcodes
  $pl = $a.places
  $nb = $a.nearby
  $links = Get-AreaLinks $a.slug
@"
      <h2>What we repair in $n</h2>
      <p>Cold Direct repairs commercial refrigeration for restaurants, pubs, bars, cafes, takeaways, hotels, staff canteens, convenience stores and production kitchens in $n. Equipment includes walk-in <a href="cold-room-repair-north-london.html">cold rooms</a>, freezer rooms, prep counters, upright fridges, chest and upright freezers, serve-over and multideck displays, bottle coolers, <a href="cellar-cooler-repair-london.html">cellar coolers</a>, commercial wine cabinets and ice machines. We provide both emergency repair and planned service. We do not invent a separate website for every keyword. Servicing is condenser cleaning, door furniture, probes and a diary so the EHO sees logs, not excuses.</p>
      <p>Most commercial faults we see in $n are the same handful: dirty condensers, failed evaporator fans, leaking door furniture, iced evaporators, weak compressors, and controllers that have lost their set point after a power dip. We diagnose on site, quote the repair before we start, and carry common Williams, Foster, Polar, Blizzard, Gram and Hoshizaki parts so first-visit fixes stay high. If a part has to be ordered, we tell you the lead time before you commit. If food is already at risk we say so before a long repair and talk through a temporary hold or a hired cabinet.</p>
      <h2>How a call-out in $n works</h2>
      <p>You call 07983 759320, 0800 112 3427 or 0203 952 4822. You speak to someone who books refrigeration work every day. Give the site name, the postcode in $pc, the make if you can see the data plate, the last safe temperature reading, and whether the fans are still turning. We will tell you whether we can attend today. Typical attendance in inner North and central London is 60 to 90 minutes. Sites south of the river or on the westbound A40 take longer. We will not invent a miracle time. We will give you a booked slot. Use the mobile after hours, the freephone from a landline on the pass, and the London office for planned PPM.</p>
      <p>On arrival we test air on and off the coil, check gaskets with a paper test, look at how stock is stacked against the evaporator, and inspect the condenser. Then we quote. Then we fix. We will not leave a room electrically unsafe. We will not ask staff to chip ice with a metal bar. Night work is standard for hospitality in $n. Put all three numbers on the duty manager board with a link to <a href="https://www.colddirect.co.uk/contact.html">https://www.colddirect.co.uk/contact</a> for email and written cabinet lists.</p>
      <h2>Keywords this $n page is built to win</h2>
      <p>Research on the live results for Cold Direct and commercial refrigeration London shows the brand already appears, but the commercial intent queries are won by dedicated area URLs: commercial refrigeration repair $n, commercial fridge repair $n, commercial refrigeration engineer $n, emergency cold room repair $n, cellar cooler repair $n, and 24/7 catering refrigeration $n. Directory pages and thin homepage mentions do not beat those URLs. This page uses British English, names $pl, and keeps every call-to-action on colddirect.co.uk.</p>
      <p>Internal links stay on this domain: <a href="index.html">homepage</a>, <a href="https://www.colddirect.co.uk/contact.html">contact</a>, <a href="commercial-fridge-repair-north-london.html">commercial fridge repair</a>, <a href="commercial-freezer-repair-north-london.html">commercial freezer repair</a>, and the cold room and cellar pages. Nearby cover includes $nb. North London 25 mile radius still applies. Multi-site operators can book more than one address on the same night if the diary allows. If the chiller room is holding but the freezer is in alarm, say which room first.</p>
      <h2>Brands and areas in $n</h2>
      <p>Williams, Foster, True, Hoshizaki, Polar, Blizzard, Gram, Lec, Snomaster, Tefcold and mixed pack systems. Ice machines include Hoshizaki and Scotsman. Send a photo of the data sticker if you want a parts check before travel. Areas covered: $pl. Postcodes $pc. Nearby $nb.</p>
      <p>Cold Direct remains commercial only. Restaurants, pubs, bars, cafes, hotels, shops, canteens and production kitchens in $n are in scope. Domestic households are not. That focus is how we keep vans stocked for trade parts instead of washing-machine belts. If you searched for Cold Direct and commercial refrigeration London, you want the firm that already owns the domain and the phone numbers, not a directory listing on someone else's site. Send a WhatsApp photo of the model plate if you want a parts check before the van leaves.</p>
      <img src="images/cold-room.webp" alt="Commercial walk-in cold room repaired by Cold Direct in $n" style="margin:20px 0;width:100%;height:280px;object-fit:cover">
      <h2>Other London commercial refrigeration pages</h2>
      <p>$links</p>
"@
}

function Get-Schema($a, $file) {
@"
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Cold Direct",
  "image": "https://www.colddirect.co.uk/images/cold-direct-logo.png",
  "url": "https://www.colddirect.co.uk/$file",
  "telephone": "+442039524822",
  "email": "info@colddirect.co.uk",
  "priceRange": "GBP",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "27 Felixstowe Road",
    "addressLocality": "Enfield",
    "addressRegion": "Greater London",
    "postalCode": "N9 0DX",
    "addressCountry": "GB"
  },
  "areaServed": { "@type": "City", "name": "$($a.name), London" },
  "openingHoursSpecification": {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "opens": "00:00",
    "closes": "23:59"
  }
}
"@
}

$counts = @()
foreach ($a in $areas) {
  $file = "commercial-refrigeration-repair-$($a.slug).html"
  $schema = Get-Schema $a $file
  $body = $a.unique + (Get-SharedBody $a)
  $plain = [regex]::Replace($body, "<[^>]+>", " ")
  $wc = ($plain -split "\s+" | Where-Object { $_ }).Count
  if ($wc -lt 800) { throw "$($a.slug) is only $wc words" }

  $html = @"
<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="favicon.ico" sizes="any">
  <link rel="icon" type="image/png" href="images/cold-direct-icon.png">
  <link rel="apple-touch-icon" href="images/cold-direct-icon.png">
  <title>$($a.title)</title>
  <meta name="description" content="$($a.meta)">
  <link rel="canonical" href="https://www.colddirect.co.uk/$file">
  <style id="light-theme">
body{background:#ffffff;color:#0a2540}
.hero,.page-header,.inner-banner{background:#f1f7ff !important;background-image:none !important;color:#0a2540 !important}
.hero:before,.page-header:before,.inner-banner:before{display:none !important}
.hero h1,.hero p,.hero .lead,.hero .kicker{color:#0a2540 !important}
.btn,.btn-light,.btn-dark,.sticky-cta a{background:#0a2540 !important;color:#ffffff !important}
.topbar,.cta-band,.site-footer,.sticky-cta{background:#f1f7ff !important;color:#0a2540 !important}
</style>
  <link rel="stylesheet" href="css/styles.css?v=navwrap1">
  <script type="application/ld+json">
$schema
  </script>
</head>
<body>
  <div class="topbar">
    <div class="wrap">
      <span>24/7 Emergency - Commercial refrigeration only</span>
      <div class="phones">
        <a href="tel:+447983759320"><span>Mobile</span> 07983 759320</a>
        <a href="tel:08001123427"><span>Freephone</span> 0800 112 3427</a>
        <a href="tel:+442039524822"><span>London Office</span> 0203 952 4822</a>
      </div>
    </div>
  </div>
  <header class="site-header">
    <div class="wrap">
      <a class="logo" href="/"><div class="logo-box"><img src="images/cold_direct_badge_logo.webp" alt="Cold Direct - Commercial Refrigeration Engineers - 24/7 Emergency Repair" width="400" height="400" fetchpriority="high"></div></a>
      <button class="nav-toggle" type="button">Menu</button>
      <nav>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="about-us.html">About</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="commercial-fridge-repair-north-london.html">Commercial fridge</a></li>
          <li><a href="commercial-freezer-repair-north-london.html">Commercial freezer</a></li>
          <li><a href="cold-room-repair-north-london.html">Cold room</a></li>
          <li><a href="freezer-room-repair-north-london.html">Freezer room</a></li>
          <li><a href="display-cabinet-repair-north-london.html">Display cabinet</a></li>
          <li><a href="cellar-cooler-repair-london.html">Cellar cooler</a></li>
          <li><a href="bottle-cooler-repair-london.html">Bottle cooler</a></li>
          <li><a href="wine-cooler-repair-london.html">Wine cooler</a></li>
          <li><a href="commercial-appliances-repair-london.html">Commercial appliances</a></li>
          <li><a href="catering-repair-london.html">Catering repair</a></li>
          <li><a href="appliances-repair-london.html">Appliances repair</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <section class="hero">
    <div class="wrap">
      <p class="kicker">$($a.kicker)</p>
      <h1>$($a.h1)</h1>
      <p class="lead">$($a.lead)</p>
      <div class="cta-row">
        <a class="btn btn-light" href="tel:+447983759320">Mobile 07983 759320</a>
        <a class="btn" href="tel:08001123427">Freephone 0800 112 3427</a>
        <a class="btn btn-dark" href="tel:+442039524822">London Office 0203 952 4822</a>
        <a class="btn" href="https://www.colddirect.co.uk/contact.html">Contact</a>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
$body
    </div>
  </section>
  <section class="cta-band">
    <div class="wrap">
      <h2>Book a commercial engineer in $($a.name)</h2>
      <p>Call any number or use <a href="https://www.colddirect.co.uk/contact.html">colddirect.co.uk/contact</a>.</p>
      <div class="phones">
        <a href="tel:+447983759320">Mobile 07983 759320</a>
        <a href="tel:08001123427">Freephone 0800 112 3427</a>
        <a href="tel:+442039524822">London Office 0203 952 4822</a>
      </div>
    </div>
  </section>
  <footer class="site-footer">
    <div class="wrap">
      <div class="grid">
        <div>
          <h3>Cold Direct</h3>
          <p>North London Commercial Refrigeration Engineers. Commercial equipment only. 24/7 emergency across a 25 mile radius.</p>
        </div>
        <div>
          <h3>Call</h3>
          <p>
            <a href="tel:+447983759320">Mobile 07983 759320</a><br>
            <a href="tel:08001123427">Freephone 0800 112 3427</a><br>
            <a href="tel:+442039524822">London Office 0203 952 4822</a><br>
            <a href="mailto:info@colddirect.co.uk">info@colddirect.co.uk</a>
          </p>
        </div>
        <div>
          <h3>More</h3>
          <p>
            <a href="index.html">Home</a><br>
            <a href="https://www.colddirect.co.uk/contact.html">Contact</a><br>
            <a href="cold-room-repair-north-london.html">Cold room</a>
          </p>
        </div>
      </div>
      <p class="legal">Commercial Refrigeration Repair $($a.name) | North London and London | 25 Mile Radius</p>
    </div>
  </footer>
  <div class="sticky-cta">
    <a href="tel:+447983759320">07983 759320</a>
    <a href="tel:08001123427">0800 112 3427</a>
    <a href="tel:+442039524822">0203 952 4822</a>
  </div>
  <script src="js/main.js"></script>
  <script src="js/booking.js"></script>
</body>
</html>
"@

  Set-Content -Path (Join-Path $root $file) -Value $html -Encoding UTF8
  if (Test-Path $mirror) {
    Set-Content -Path (Join-Path $mirror $file) -Value $html -Encoding UTF8
  }
  $counts += "$file $wc words"
}

$sitemap = Join-Path $root "sitemap.xml"
$sx = Get-Content $sitemap -Raw
foreach ($a in $areas) {
  $loc = "https://www.colddirect.co.uk/commercial-refrigeration-repair-$($a.slug).html"
  if ($sx -notmatch [regex]::Escape($loc)) {
    $block = "  <url>`r`n    <loc>$loc</loc>`r`n    <lastmod>2026-09-06</lastmod>`r`n    <changefreq>weekly</changefreq>`r`n    <priority>0.8</priority>`r`n  </url>`r`n"
    $sx = $sx -replace "</urlset>", ($block + "</urlset>")
  }
}
Set-Content $sitemap -Value $sx -Encoding UTF8
if (Test-Path (Join-Path $mirror "sitemap.xml")) {
  Set-Content (Join-Path $mirror "sitemap.xml") -Value $sx -Encoding UTF8
}

$idx = Join-Path $root "index.html"
$it = Get-Content $idx -Raw
$map = @{
  "<li>Camden</li>" = '<li><a href="commercial-refrigeration-repair-camden.html">Camden</a></li>'
  "<li>Islington</li>" = '<li><a href="commercial-refrigeration-repair-islington.html">Islington</a></li>'
  "<li>Hackney</li>" = '<li><a href="commercial-refrigeration-repair-hackney.html">Hackney</a></li>'
  "<li>Haringey</li>" = '<li><a href="commercial-refrigeration-repair-haringey.html">Haringey</a></li>'
  "<li>City of London</li>" = '<li><a href="commercial-refrigeration-repair-city-of-london.html">City of London</a></li>'
  "<li>Westminster</li>" = '<li><a href="commercial-refrigeration-repair-westminster.html">Westminster</a></li>'
  "<li>Stratford</li>" = '<li><a href="commercial-refrigeration-repair-newham.html">Stratford</a></li>'
}
foreach ($k in $map.Keys) {
  if ($it.Contains($k) -and -not $it.Contains($map[$k])) { $it = $it.Replace($k, $map[$k]) }
}
Set-Content $idx -Value $it -Encoding UTF8
$counts
Write-Output "done $($areas.Count) pages"
