<%@ Page Language="C#" Debug="true" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.Text.RegularExpressions" %>
<%@ Import Namespace="System.Collections.Generic" %>
<script runat="server">
protected void Page_Load(object sender, EventArgs e)
{
    // V4.9.1: the access key is NOT in source control. It is read from App_Data/auto-seo.key on the server
    // (never served over HTTP, never in git). Fail closed: missing/short key file = everything is rejected.
    string expectedKey = "";
    try { string keyFile = Server.MapPath("~/App_Data/auto-seo.key"); if (File.Exists(keyFile)) expectedKey = File.ReadAllText(keyFile).Trim(); } catch { }
    string suppliedKey = Request.QueryString["key"] ?? "";
    if (expectedKey.Length < 24 || !KeysEqual(suppliedKey, expectedKey)) { Response.StatusCode = 403; Response.Write("403"); return; }
    string root = Server.MapPath("~/");

    string footerBlock = "\r\n<!-- AUTO-SEO-V4-2026 -->\r\n" +
        "<div class=\"seo-service-tags\" style=\"font-size:12px;color:#666;padding:12px 15px;text-align:center;border-top:1px solid #eee;margin-top:20px;\">\r\n" +
        "  <strong>24/7 London Commercial Refrigeration, Cellar &amp; Catering Repair Services:</strong>\r\n" +
        "  <a href=\"/commercial-fridge-repair-london/\" style=\"color:#555;margin:0 6px;\">Commercial Fridge Repair London</a> |\r\n" +
        "  <a href=\"/commercial-freezer-repair-london/\" style=\"color:#555;margin:0 6px;\">Commercial Freezer Repair London</a> |\r\n" +
        "  <a href=\"/cold-room-repair-london/\" style=\"color:#555;margin:0 6px;\">Cold Room Repair London</a> |\r\n" +
        "  <a href=\"/cellar-cooler-repair-london.asp\" style=\"color:#555;margin:0 6px;\">Cellar Repair London</a> |\r\n" +
        "  <a href=\"/catering-repair-london/\" style=\"color:#555;margin:0 6px;\">Catering Repair London</a> |\r\n" +
        "  <a href=\"/commercial-catering-repair-london/\" style=\"color:#555;margin:0 6px;\">Commercial Catering Repair London</a> |\r\n" +
        "  <a href=\"/air-conditioning-repair-london/\" style=\"color:#555;margin:0 6px;\">Air Conditioning Repair London</a> |\r\n" +
        "  <a href=\"/fridge-repair-london/\" style=\"color:#555;margin:0 6px;\">Fridge Repair London</a> |\r\n" +
        "  <a href=\"/freezer-repair-london/\" style=\"color:#555;margin:0 6px;\">Freezer Repair London</a>\r\n" +
        "</div>\r\n";

    string scOpen = "<scr" + "ipt type=\"application/ld+json\">";
    string scClose = "</scr" + "ipt>";
    string schemaBlock = "\r\n<!-- AUTO-SEO-V4-SCHEMA -->\r\n" + scOpen + "\r\n{\r\n" +
        "  \"@context\": \"https://schema.org\",\r\n" +
        "  \"@type\": \"HVACBusiness\",\r\n" +
        "  \"@id\": \"https://www.colddirect.co.uk/#business\",\r\n" +
        "  \"name\": \"Cold Direct Commercial Refrigeration, Cold Room, Cellar & Catering Repair London\",\r\n" +
        "  \"url\": \"https://www.colddirect.co.uk/\",\r\n" +
        "  \"telephone\": \"+442039524822\",\r\n" +
        "  \"priceRange\": \"\u00A3\u00A3\",\r\n" +
        "  \"address\": {\r\n" +
        "    \"@type\": \"PostalAddress\",\r\n" +
        "    \"streetAddress\": \"27 Felixstowe Road\",\r\n" +
        "    \"addressLocality\": \"Enfield, London\",\r\n" +
        "    \"postalCode\": \"N9 0DX\",\r\n" +
        "    \"addressCountry\": \"GB\"\r\n" +
        "  },\r\n" +
        "  \"geo\": {\r\n" +
        "    \"@type\": \"GeoCoordinates\",\r\n" +
        "    \"latitude\": \"51.6256\",\r\n" +
        "    \"longitude\": \"-0.0561\"\r\n" +
        "  },\r\n" +
        "  \"areaServed\": \"London\"\r\n" +
        "}\r\n" + scClose + "\r\n";

    // V4.7: unified #business node shared by the homepage and the 9 money pages
    string bizNodeJson =
        "    {\r\n" +
        "      \"@type\": [\r\n" +
        "        \"HVACBusiness\",\r\n" +
        "        \"LocalBusiness\"\r\n" +
        "      ],\r\n" +
        "      \"@id\": \"https://www.colddirect.co.uk/#business\",\r\n" +
        "      \"name\": \"Cold Direct Commercial Refrigeration, Cold Room, Cellar & Catering Repair London\",\r\n" +
        "      \"url\": \"https://www.colddirect.co.uk/\",\r\n" +
        "      \"image\": \"https://www.colddirect.co.uk/images/logo/colddirect-main.webp\",\r\n" +
        "      \"telephone\": \"+442039524822\",\r\n" +
        "      \"contactPoint\": [\r\n" +
        "        {\r\n" +
        "          \"@type\": \"ContactPoint\",\r\n" +
        "          \"telephone\": \"+448001123427\",\r\n" +
        "          \"contactType\": \"customer service\",\r\n" +
        "          \"areaServed\": \"GB\"\r\n" +
        "        },\r\n" +
        "        {\r\n" +
        "          \"@type\": \"ContactPoint\",\r\n" +
        "          \"telephone\": \"+447983759320\",\r\n" +
        "          \"contactType\": \"emergency service\",\r\n" +
        "          \"areaServed\": \"GB\"\r\n" +
        "        }\r\n" +
        "      ],\r\n" +
        "      \"priceRange\": \"\u00A3\u00A3\",\r\n" +
        "      \"address\": {\r\n" +
        "        \"@type\": \"PostalAddress\",\r\n" +
        "        \"streetAddress\": \"27 Felixstowe Road\",\r\n" +
        "        \"addressLocality\": \"Enfield, London\",\r\n" +
        "        \"postalCode\": \"N9 0DX\",\r\n" +
        "        \"addressCountry\": \"GB\"\r\n" +
        "      },\r\n" +
        "      \"geo\": {\r\n" +
        "        \"@type\": \"GeoCoordinates\",\r\n" +
        "        \"latitude\": \"51.6256\",\r\n" +
        "        \"longitude\": \"-0.0561\"\r\n" +
        "      },\r\n" +
        "      \"areaServed\": [\r\n" +
        "        \"London\",\r\n" +
        "        {\r\n" +
        "          \"@type\": \"GeoCircle\",\r\n" +
        "          \"geoMidpoint\": {\r\n" +
        "            \"@type\": \"GeoCoordinates\",\r\n" +
        "            \"latitude\": \"51.6256\",\r\n" +
        "            \"longitude\": \"-0.0561\"\r\n" +
        "          },\r\n" +
        "          \"geoRadius\": \"40234\"\r\n" +
        "        }\r\n" +
        "      ],\r\n" +
        "      \"aggregateRating\": {\r\n" +
        "        \"@type\": \"AggregateRating\",\r\n" +
        "        \"ratingValue\": \"4.9\",\r\n" +
        "        \"reviewCount\": \"38\",\r\n" +
        "        \"bestRating\": \"5\"\r\n" +
        "      },\r\n" +
        "      \"openingHoursSpecification\": {\r\n" +
        "        \"@type\": \"OpeningHoursSpecification\",\r\n" +
        "        \"dayOfWeek\": [\r\n" +
        "          \"Monday\",\r\n" +
        "          \"Tuesday\",\r\n" +
        "          \"Wednesday\",\r\n" +
        "          \"Thursday\",\r\n" +
        "          \"Friday\",\r\n" +
        "          \"Saturday\",\r\n" +
        "          \"Sunday\"\r\n" +
        "        ],\r\n" +
        "        \"opens\": \"00:00\",\r\n" +
        "        \"closes\": \"23:59\"\r\n" +
        "      }\r\n" +
        "    }\r\n";

    string schemaBlockCore = "\r\n<!-- AUTO-SEO-V4-SCHEMA -->\r\n" + scOpen + "\r\n{\r\n  \"@context\": \"https://schema.org\",\r\n  \"@graph\": [\r\n" + bizNodeJson + "\r\n  ]\r\n}\r\n" + scClose + "\r\n";

    // V4.7 money pages: [0]=title [1]=meta description [2]=Service name [3]=serviceType [4..]=OfferCatalog keyword variations
    Dictionary<string, string[]> moneyMeta = new Dictionary<string, string[]>();
    moneyMeta["fridge-repair-london"] = new string[] { "Fridge Repair London | Same-Day 24/7 Emergency Engineers", "Fridge repair London for restaurants, pubs and shops: same-day 24/7 emergency repairs and service, fixed diagnostic call-out. Call 07983 759320.", "Fridge repair London", "Commercial fridge repair", "Fridge repair London", "Fridge repairs London", "Fridge service London", "Emergency fridge repair London", "Commercial fridge repair", "Same day fridge repair London", "24 hour emergency fridge repair London", "Affordable fridge repair London with fixed diagnostic call-out" };
    moneyMeta["freezer-repair-london"] = new string[] { "Freezer Repair London | Same-Day 24/7 Emergency Engineers", "Freezer repair London for kitchens, bars and shops: same-day 24/7 emergency repairs and service, fixed diagnostic call-out. Call 07983 759320.", "Freezer repair London", "Commercial freezer repair", "Freezer repair London", "Freezer repairs London", "Freezer service London", "Emergency freezer repair London", "Commercial freezer repair", "Same day freezer repair London", "24 hour emergency freezer repair London", "Affordable freezer repair London with fixed diagnostic call-out" };
    moneyMeta["commercial-fridge-repair-london"] = new string[] { "Commercial Fridge Repair London | 24/7 Emergency Same-Day Engineers", "Commercial fridge repair London: 24/7 emergency and same-day repairs, fixed diagnostic call-out, F-Gas certified London engineers. Call 07983 759320.", "Commercial fridge repair London", "Commercial fridge repair", "Commercial fridge repair London", "Commercial fridge repairs", "Commercial fridge service", "Walk-in chiller repair London", "Display chiller repair London", "Emergency fridge repair", "Same day commercial fridge repair London", "24 hour emergency commercial fridge repair London", "Affordable commercial fridge repair London with fixed diagnostic call-out" };
    moneyMeta["commercial-freezer-repair-london"] = new string[] { "Commercial Freezer Repair London | 24/7 Emergency Same-Day Engineers", "Commercial freezer repair London: 24/7 emergency and same-day repairs, fixed diagnostic call-out, walk-in and kitchen freezers. Call 07983 759320.", "Commercial freezer repair London", "Commercial freezer repair", "Commercial freezer repair London", "Commercial freezer repairs", "Commercial freezer service", "Walk-in freezer repair London", "Emergency commercial freezer repair", "Same day commercial freezer repair London", "24 hour emergency commercial freezer repair London", "Affordable commercial freezer repair London with fixed diagnostic call-out" };
    moneyMeta["cold-room-repair-london"] = new string[] { "Cold Room Repair London | 24/7 Same-Day Emergency Repairs", "Cold room repair London: 24/7 same-day emergency repairs and service by London engineers. Affordable, fixed diagnostic call-out. Call 07983 759320.", "Cold room repair London", "Walk-in cold room repair", "Cold room repair London", "Cold room repairs London", "Cold room repair near me", "Cold room service London", "Emergency cold room repair", "Walk-in chiller repair London", "Same day cold room repair London", "24 hour emergency cold room repair London", "Affordable cold room repair London with fixed diagnostic call-out" };
    moneyMeta["catering-repair-london"] = new string[] { "Catering Repair London | Same-Day 24/7 Emergency Kitchen Engineers", "Catering repair London for restaurant and takeaway kitchens: same-day 24/7 emergency repairs and service, fixed diagnostic call-out. Call 07983 759320.", "Catering repair London", "Commercial catering refrigeration repair", "Catering repair London", "Commercial catering repair", "Catering fridge repair", "Catering refrigeration service London", "Kitchen chiller repair London", "Same day catering repair London", "24 hour emergency catering repair London", "Affordable catering repair London with fixed diagnostic call-out" };
    moneyMeta["commercial-appliances-repair-london"] = new string[] { "Commercial Catering Repair London | 24/7 Same-Day Engineers", "Commercial catering repair London: 24/7 same-day emergency repairs and service for kitchen refrigeration and ice machines. Fixed call-out. 07983 759320.", "Commercial catering and refrigeration appliances repair London", "Commercial refrigeration appliances repair", "Commercial catering repair", "Catering refrigeration appliances repair", "Commercial appliances repair London", "Commercial kitchen refrigeration repair", "Emergency commercial appliances repair", "Same day commercial catering repair London", "24 hour emergency commercial catering repair London", "Affordable commercial catering repair London with fixed diagnostic call-out" };
    moneyMeta["air-conditioning-repair-london"] = new string[] { "Air Conditioning Repair London | 24/7 Same-Day Emergency AC", "Air conditioning repair London for offices, shops and server rooms: 24/7 same-day emergency repairs, fixed diagnostic call-out. Call 07983 759320.", "Air conditioning repair London", "Commercial air conditioning repair", "Air conditioning repair London", "Commercial air conditioning repair London", "Emergency AC repair near me", "AC servicing London", "VRV VRF repair London", "Same day air conditioning repair London", "24 hour emergency air conditioning repair London", "Affordable air conditioning repair London with fixed diagnostic call-out" };
    moneyMeta["cellar-cooler-repair-london"] = new string[] { "Cellar Repair London | Same-Day 24/7 Pub and Bar Cooler Engineers", "Cellar repair London for pubs and bars: same-day 24/7 emergency cellar cooler repairs and service, fixed diagnostic call-out. Call 07983 759320.", "Cellar repair London", "Cellar cooler repair", "Cellar repair", "Cellar repair London", "Cellar cooler repair London", "Pub & bar cellar cooling repair", "Beer cellar cooler repair London", "Same day cellar repair London", "24 hour emergency cellar cooler repair London", "Affordable cellar repair London with fixed diagnostic call-out" };


    // V4.10 area pages + de-duplicated service pages (55-65 chars): unique [0]=title [1]=meta description per borough/suburb (single source of truth; tools/area_titles_apply.py mirrors it into the HTML)
    Dictionary<string, string[]> areaMeta = new Dictionary<string, string[]>();
    areaMeta["cold-room-repair-north-london"] = new string[] { "Cold Room Repair North London | Enfield, Barnet & Camden", "24/7 cold room repair in North London. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-barnet"] = new string[] { "Cold Room Repair Barnet | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Barnet. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-edgware"] = new string[] { "Cold Room Repair Edgware | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Edgware. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-enfield"] = new string[] { "Cold Room Repair Enfield | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Enfield. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-finchley"] = new string[] { "Cold Room Repair Finchley | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Finchley. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-harrow"] = new string[] { "Cold Room Repair Harrow | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Harrow. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-palmers-green"] = new string[] { "Cold Room Repair Palmers Green | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Palmers Green. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-southgate"] = new string[] { "Cold Room Repair Southgate | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Southgate. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-tottenham"] = new string[] { "Cold Room Repair Tottenham | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Tottenham. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-wembley"] = new string[] { "Cold Room Repair Wembley | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Wembley. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["cold-room-repair-wood-green"] = new string[] { "Cold Room Repair Wood Green | 24/7 Walk-In Chiller Engineers", "24/7 cold room repair in Wood Green. Same-day F-Gas engineers for walk-in chiller & freezer rooms, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["commercial-fridge-repair-central-london"] = new string[] { "Commercial Fridge Repair Central London | 24/7 Soho & City", "Commercial fridge repair in Central London: 24/7 same-day F-Gas engineers for Soho, West End, City & Holborn restaurants, bars & hotels. Call 07983 759320." };
    areaMeta["commercial-fridge-repair-east-london"] = new string[] { "Commercial Fridge Repair East London | Shoreditch & Wharf", "Commercial fridge repair in East London: same-day F-Gas engineers for Shoreditch, Canary Wharf, Stratford & Hackney kitchens, bars & shops. Call 07983 759320." };
    areaMeta["commercial-fridge-repair-north-london"] = new string[] { "Commercial Fridge Repair North London | Enfield & Barnet", "Commercial fridge repair in North London: 24/7 same-day F-Gas engineers covering Enfield, Barnet, Camden & Islington kitchens and shops. Call 0203 952 4822." };
    areaMeta["commercial-fridge-repair-enfield"] = new string[] { "Commercial Fridge Repair Enfield | 24/7 Same-Day Engineers", "Commercial fridge repair in Enfield: 24/7 same-day F-Gas engineers for restaurants, takeaways, shops & warehouses in Enfield & Southgate. Call 0203 952 4822." };
    areaMeta["commercial-freezer-repair-north-london"] = new string[] { "Commercial Freezer Repair North London | 24/7 Engineers", "Commercial freezer repair in North London: 24/7 F-Gas engineers for kitchen, walk-in & display freezers in Enfield, Barnet & Camden. Call 0203 952 4822." };
    areaMeta["commercial-freezer-repair-tottenham"] = new string[] { "Commercial Freezer Repair Tottenham | 24/7 Same-Day Engineers", "Commercial freezer repair in Tottenham: 24/7 same-day F-Gas engineers for restaurants, shops & warehouses in Tottenham, Haringey & Edmonton. Call 0203 952 4822." };
    areaMeta["blast-chiller-repair-north-london"] = new string[] { "Blast Chiller Repair North London | 24/7 Kitchen Engineers", "Blast chiller & blast freezer repair in North London: 24/7 same-day F-Gas engineers for commercial kitchens in Enfield, Barnet & Camden. Call 0203 952 4822." };
    areaMeta["chiller-repair-north-london"] = new string[] { "Chiller Repair North London | Walk-In & Display Chillers", "Chiller repair in North London: 24/7 same-day F-Gas engineers for walk-in, multideck & display chillers across Enfield, Barnet & Camden. Call 0203 952 4822." };
    areaMeta["blast-chiller-repair-london"] = new string[] { "Blast Chiller Repair London | 24/7 Commercial Engineers", "24/7 emergency blast chiller repair in London. Same-day F-Gas commercial kitchen engineers for Williams, Foster & Irinox blast chillers. Call 0203 952 4822." };
    areaMeta["blast-freezer-repair-london"] = new string[] { "Blast Freezer Repair London | 24/7 Same-Day Engineers", "24/7 emergency blast freezer repair in London. Same-day F-Gas engineers for commercial kitchen blast freezers, shock freezers & cabinets. Call 0203 952 4822." };
    areaMeta["blast-freezing"] = new string[] { "Blast Freezing & Blast Chilling Service London | ColdDirect", "Blast freezing & blast chilling equipment service in London. F-Gas certified engineers for commercial kitchens, caterers & food producers. Call 0203 952 4822." };
    areaMeta["commercial-blast-chiller-repair-london"] = new string[] { "Commercial Blast Chiller Repair London | Kitchen Specialists", "Commercial blast chiller repair in London for restaurants, hotels & contract caterers. Same-day F-Gas engineers, fixed-price diagnosis. Call 0203 952 4822." };
    areaMeta["commercial-blast-freezer-repair-london"] = new string[] { "Commercial Blast Freezer Repair London | Kitchen Specialists", "Commercial blast freezer repair in London for restaurants, hotels & food producers. Same-day F-Gas engineers, fixed-price diagnosis. Call 0203 952 4822." };
    areaMeta["chiller-repair-london"] = new string[] { "Chiller Repair London | 24/7 Walk-In & Display Chillers", "24/7 commercial chiller repair in London. Fast 60-90 min response for walk-in chillers, multideck display chillers & cellar coolers. Call 0203 952 4822." };
    areaMeta["chiller-repairs-london"] = new string[] { "Chiller Repairs London | Same-Day Commercial Chiller Service", "Chiller repairs in London: same-day commercial chiller service & repair by F-Gas certified engineers for kitchens, shops & venues. Call 0203 952 4822." };
    areaMeta["walk-in-chiller-repair"] = new string[] { "Walk-In Chiller Repair London | Cold Room Chiller Engineers", "Walk-in chiller repair in London: 24/7 F-Gas engineers for walk-in chiller rooms, evaporators, compressors & gas leaks. Call 0203 952 4822." };
    areaMeta["adexa-fridge-repair-london"] = new string[] { "Adexa Fridge Repair London | 24/7 Commercial Engineers", "24/7 emergency Adexa commercial fridge repair in London. Same-day F-Gas engineers for Adexa cabinets, counters & display fridges. Call 0203 952 4822." };
    areaMeta["cabinet-fridge-repair-london"] = new string[] { "Cabinet Fridge Repair London | 24/7 Commercial Engineers", "24/7 emergency commercial cabinet fridge repair in London. Same-day F-Gas engineers for upright kitchen cabinets & gastronorm fridges. Call 0203 952 4822." };
    areaMeta["empire-fridge-repair-london"] = new string[] { "Empire Fridge Repair London | 24/7 Commercial Engineers", "24/7 emergency Empire commercial fridge repair in London. Same-day F-Gas engineers for Empire cabinets, counters & display fridges. Call 0203 952 4822." };
    areaMeta["multideck-fridge-repair-london"] = new string[] { "Multideck Fridge Repair London | 24/7 Supermarket Engineers", "24/7 emergency multideck fridge repair in London. Same-day F-Gas engineers for supermarket & convenience store multidecks. Call 0203 952 4822." };
    areaMeta["undercounter-fridge-repair-london"] = new string[] { "Undercounter Fridge Repair London | Commercial Kitchens", "24/7 emergency commercial undercounter fridge repair in London. Same-day F-Gas engineers for bar & kitchen undercounter fridges. Call 0203 952 4822." };
    areaMeta["walk-in-fridge-repair-london"] = new string[] { "Walk-In Fridge Repair London | 24/7 Cold Room Engineers", "24/7 walk-in fridge repair in London. Same-day F-Gas engineers for commercial walk-in fridges & cold rooms, compressors & gas leaks. Call 0203 952 4822." };

    // V4.8: pages with no title/description rule (about, news) must still end up with a non-empty meta description.
    // Fill-only: an existing non-empty description is NEVER overwritten (owner can edit these pages by hand).
    Dictionary<string, string> fallbackDesc = new Dictionary<string, string>();
    fallbackDesc["about"] = "About Cold Direct: London commercial refrigeration experts. 24/7 fridge, freezer, cold room &amp; cellar repair by F-Gas certified engineers. Call 0203 952 4822.";
    fallbackDesc["news"] = "Cold Direct advice &amp; news: commercial fridge, freezer &amp; cold room repair guides, F-Gas updates and maintenance tips for London. Call 0203 952 4822.";


    List<string> filesList = new List<string>();
    try { filesList.AddRange(Directory.GetFiles(root, "*.html", SearchOption.TopDirectoryOnly)); } catch { }
    try
    {
        foreach (string dir in Directory.GetDirectories(root, "*", SearchOption.TopDirectoryOnly))
        {
            string dn = Path.GetFileName(dir).ToLowerInvariant();
            if (dn.StartsWith(".") || dn.StartsWith("_") || dn.Contains("backup") || dn.Contains("plesk") || dn.Contains("stat") || dn.Equals("logs", StringComparison.OrdinalIgnoreCase) || dn.Contains("error") || dn == "colddirect-public-html" || dn == "node_modules" || dn == "cgi-bin" || dn == "app_data") continue;
            try { filesList.AddRange(Directory.GetFiles(dir, "*.html", SearchOption.AllDirectories)); } catch { }
        }
    }
    catch { }

    // V4.9: URLs that web.config 301-redirects to another page must never be sitemap URLs
    HashSet<string> redirectedSlugs = new HashSet<string>(new string[] { "about", "news", "refrigeration-brands-repairs-london",
        // blog posts 301-redirected by .htaccess (domestic / retired topics): the .html files still exist on disk
        "smeg-fridge-freezer-control-panel", "samsung-fridge-freezer-not-freezing", "best-ice-cream-makers",
        "cold-room-troubleshooting", "chiller-not-cooling" });

    int updated = 0;
    List<string> changedFiles = new List<string>();   // diagnostics: which files were rewritten and where they first differ
    List<string> sitemapUrls = new List<string>();
    sitemapUrls.Add("https://www.colddirect.co.uk/");

    foreach (string file in filesList)
    {
        try
        {
            string rel = file.Substring(root.Length).Replace("\\", "/").ToLowerInvariant();
            if (rel.StartsWith("_") || rel.Contains("backup") || rel.Contains("404") || rel.Contains("colddirect-public-html/") || rel.StartsWith("logs/") || rel.StartsWith("plesk-") || rel.StartsWith("error_docs/") || rel.StartsWith("google")) continue;

            // Build clean sitemap URL list — exclude dishwasher & non-indexable pages
            if (!rel.Contains("dishwasher") && !rel.Contains("admin") && !rel.Contains("test"))
            {
                if (rel.EndsWith("/index.html"))
                {
                    string folderUrl = "https://www.colddirect.co.uk/" + rel.Substring(0, rel.Length - 10);
                    if (!sitemapUrls.Contains(folderUrl)) sitemapUrls.Add(folderUrl);
                }
                else if (!rel.Contains("/") && rel != "index.html")
                {
                    string slugUrl = "https://www.colddirect.co.uk/" + rel.Replace(".html", "/");
                    if (!sitemapUrls.Contains(slugUrl)) sitemapUrls.Add(slugUrl);
                }
            }

            if (rel.Contains("dishwasher")) continue;

            string html = File.ReadAllText(file, Encoding.UTF8);
            string orig = html;
            string name = Path.GetFileNameWithoutExtension(file).ToLowerInvariant();
            if (name == "index" && rel.Contains("/"))
            {
                string[] parts = rel.Split('/');
                if (parts.Length >= 2) name = parts[parts.Length - 2];
            }

            // Strip any UTF-8 mojibake (Â£ / Â°)
            if (html.Contains("\u00C2\u00A3")) html = html.Replace("\u00C2\u00A3", "\u00A3");
            if (html.Contains("\u00C2\u00B0")) html = html.Replace("\u00C2\u00B0", "\u00B0");
            // V4.5: repair double-encoded dashes / quotes
            if (html.Contains("\u00E2\u20AC\u201D")) html = html.Replace("\u00E2\u20AC\u201D", "\u2014");
            if (html.Contains("\u00E2\u20AC\u201C")) html = html.Replace("\u00E2\u20AC\u201C", "\u2013");
            if (html.Contains("\u00E2\u20AC\u0153")) html = html.Replace("\u00E2\u20AC\u0153", "\u201C");
            if (html.Contains("\u00E2\u20AC\u009D")) html = html.Replace("\u00E2\u20AC\u009D", "\u201D");
            if (html.Contains("\u00E2\u20AC\u2122")) html = html.Replace("\u00E2\u20AC\u2122", "\u2019");
            if (html.Contains("\u00C2\u00A3\u00C2\u00A3")) html = html.Replace("\u00C2\u00A3\u00C2\u00A3", "\u00A3\u00A3");
            bool isCore = (rel == "index.html" || moneyMeta.ContainsKey(name));
            // V4.7: keep noindex pages and pages canonicalised to another URL out of sitemap.xml
            if (rel != "index.html")
            {
                string selfUrl = rel.EndsWith("/index.html") ? "https://www.colddirect.co.uk/" + rel.Substring(0, rel.Length - 10) : "https://www.colddirect.co.uk/" + rel.Replace(".html", "/");
                Match canonMatch = Regex.Match(html, "<link[^>]+rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)[\"']", RegexOptions.IgnoreCase);
                bool noindexPage = Regex.IsMatch(html, "<meta[^>]+name=[\"']robots[\"'][^>]*content=[\"'][^\"']*noindex", RegexOptions.IgnoreCase);
                bool canonElsewhere = canonMatch.Success && NormUrl(canonMatch.Groups[1].Value) != NormUrl(selfUrl);
                // V4.8: meta-refresh redirect stubs are never sitemap URLs
                bool refreshStub = Regex.IsMatch(html, "<meta[^>]+http-equiv=[\"']refresh[\"']", RegexOptions.IgnoreCase);
                bool redirectedAway = redirectedSlugs.Contains(name);
                if (noindexPage || canonElsewhere || refreshStub || redirectedAway) sitemapUrls.Remove(selfUrl);
            }

            // V4.9: /blog/ articles keep their own layout. No title/description rewrite, no V4 footer/schema/bloghub
            // injection, no mojibake rewrite. The ONLY write allowed is a fill-only description when it is empty/missing.
            if (rel.StartsWith("blog/"))
            {
                html = orig;
                bool blogHasDesc = Regex.IsMatch(html, "<meta[^>]+name=[\"']description[\"'][^>]*content=[\"']\\s*[^\"'\\s]", RegexOptions.IgnoreCase)
                                || Regex.IsMatch(html, "<meta[^>]+content=[\"']\\s*[^\"'\\s][^>]*name=[\"']description[\"']", RegexOptions.IgnoreCase);
                if (!blogHasDesc && !html.Contains("<!-- AUTO-SEO-LOCKED -->"))
                {
                    Match tm = Regex.Match(html, @"<title>([\s\S]*?)</title>", RegexOptions.IgnoreCase);
                    string tt = tm.Success ? Regex.Replace(tm.Groups[1].Value, @"\s+", " ").Trim() : "";
                    int bar = tt.IndexOf('|'); if (bar > 10) tt = tt.Substring(0, bar).Trim();
                    string tail = " Cold Direct commercial refrigeration guide for London. Call 0203 952 4822.";
                    if (tt.Length > 0)
                    {
                        string bd = tt.TrimEnd('.', ' ') + "." + tail;
                        if (bd.Length > 160) bd = tt.Substring(0, Math.Min(tt.Length, 160 - tail.Length - 1)).TrimEnd('.', ' ', ',') + "." + tail;
                        bd = bd.Replace("&", "&amp;").Replace("\"", "&quot;");
                        html = Regex.Replace(html, "<meta[^>]+name=[\"']description[\"'][^>]*>", "", RegexOptions.IgnoreCase);
                        html = new Regex("</title>", RegexOptions.IgnoreCase).Replace(html, "</title>" + (orig.Contains("\r\n") ? "\r\n" : "\n") + "  <meta name=\"description\" content=\"" + bd + "\">", 1);
                    }
                }
                if (ContentDiffers(orig, html)) { File.WriteAllText(file, html, new UTF8Encoding(false)); updated++; changedFiles.Add(DescribeDiff(rel, orig, html)); }
                continue;
            }

            // Upgrade old V4 blocks cleanly
            html = Regex.Replace(html, @"\s*<!-- AUTO-SEO-V[234]-2026 -->[\s\S]*?</div>\s*", "");
            html = Regex.Replace(html, "\\s*<!-- AUTO-SEO-V[345]-SCHEMA -->[\\s\\S]*?" + scClose + "\\s*", "");

            if (!html.Contains("<!-- AUTO-SEO-LOCKED -->") && !rel.StartsWith("blog/"))
            {
                string newTitle = "";
                string newDesc = "";

                if (rel == "index.html") {
                    newTitle = "Commercial Refrigeration & Air Conditioning Engineers London | ColdDirect";
                    newDesc = "Commercial refrigeration & air conditioning engineers in London. 24/7 emergency repair & service, fixed-rate quotes, F-Gas certified. Call 0203 952 4822.";
                } else if (moneyMeta.ContainsKey(name)) {
                    newTitle = moneyMeta[name][0];
                    newDesc = moneyMeta[name][1];
                } else if (areaMeta.ContainsKey(name)) {
                    newTitle = areaMeta[name][0];
                    newDesc = areaMeta[name][1];
                } else if (name.Contains("dairy-cabinet")) {
                    newTitle = "Dairy Cabinet Repair London | 24/7 Multideck & Display Chiller Engineers";
                    newDesc = "Emergency dairy cabinet repair in London. 24/7 same-day F-Gas engineers for milk multidecks, cheese serve-overs & retail display chillers. 60\u201390 min response. Call 0203 952 4822.";
                } else if (name.Contains("cellar")) {
                    newTitle = "Cellar Cooling Repair London | 24/7 Pub & Bar Beer Chiller Engineers";
                    newDesc = "24/7 emergency beer cellar cooling & pub cellar cooler repair in London. Same-day F-Gas engineers for pubs, bars & hospitality venues. 60\u201390 min response. Call 0203 952 4822.";
                } else if (name.Contains("blast-freezer") || name.Contains("blast-chiller") || name.Contains("blast-freezing")) {
                    newTitle = "Blast Freezer & Chiller Repair London | 24/7 Commercial Kitchen Engineers";
                    newDesc = "24/7 emergency blast chiller & blast freezer repair in London. Same-day F-Gas commercial kitchen engineers for Williams, Foster & Irinox units. Call 0203 952 4822.";
                } else if (name.Contains("supermarket-freezer")) {
                    newTitle = "Supermarket Freezer Repair London | 24/7 Commercial Display & Island Engineers";
                    newDesc = "24/7 emergency supermarket freezer repair in London. Same-day F-Gas engineers for glass-door freezers, chest islands & remote pack systems. Call 0203 952 4822.";
                } else if (name.Contains("supermarket")) {
                    newTitle = "Supermarket Fridge & Freezer Repair London | 24/7 Multideck Engineers";
                    newDesc = "24/7 emergency supermarket fridge & multideck chiller repair in London. Same-day F-Gas engineers for retail display cases & remote packs. Call 0203 952 4822.";
                } else if (name.Contains("williams-freezer")) {
                    newTitle = "Williams Freezer Repair London | 24/7 Commercial Kitchen Engineers";
                    newDesc = "24/7 emergency Williams commercial freezer repair in London. Same-day F-Gas engineers for Williams Jade uprights, undercounters & blast freezers. Call 0203 952 4822.";
                } else if (name.Contains("williams-fridge") || name == "williams") {
                    newTitle = "Williams Fridge Repair London | 24/7 Commercial Catering Engineers";
                    newDesc = "24/7 emergency Williams commercial fridge repair in London. Same-day F-Gas engineers for Williams Jade gastronorm uprights, prep counters & chillers. Call 0203 952 4822.";
                } else if (name.Contains("liebherr")) {
                    newTitle = "Liebherr Commercial Fridge Repair London | 24/7 Same-Day Engineers";
                    newDesc = "24/7 emergency Liebherr commercial fridge & freezer repair in London. Same-day F-Gas engineers for restaurant, hotel, bakery & medical cabinets. Call 0203 952 4822.";
                } else if (name.Contains("ice-o-matic")) {
                    newTitle = "Ice-O-Matic Ice Machine Repair London | 24/7 Commercial Engineers";
                    newDesc = "24/7 emergency Ice-O-Matic commercial ice machine repair in London. Same-day F-Gas engineers for cube & flake ice makers in bars, hotels & restaurants. Call 0203 952 4822.";
                } else if (name.Contains("hoshizaki")) {
                    newTitle = "Hoshizaki Ice Machine Repair London | 24/7 Commercial Ice Maker Engineers";
                    newDesc = "24/7 emergency Hoshizaki commercial ice machine & fridge repair in London. Same-day engineers for KM/IM cube & flake ice makers. Call 0203 952 4822.";
                } else if (name.Contains("subzero-freezer")) {
                    newTitle = "Sub-Zero Freezer Repair London | 24/7 Emergency Commercial Engineers";
                    newDesc = "24/7 emergency commercial Sub-Zero freezer repair in London. Same-day F-Gas engineers for hospitality & commercial venues. Call 0203 952 4822.";
                } else if (name.Contains("subzero-fridge")) {
                    newTitle = "Sub-Zero Fridge Repair London | 24/7 Emergency Commercial Engineers";
                    newDesc = "24/7 emergency commercial Sub-Zero fridge repair in London. Same-day F-Gas engineers for hospitality & commercial kitchens. Call 0203 952 4822.";
                } else if (name.Contains("foster-freezer")) {
                    newTitle = "Foster Freezer Repair London | 24/7 Commercial Kitchen Engineers";
                    newDesc = "24/7 emergency Foster commercial freezer repair in London. Same-day F-Gas engineers for Foster EcoPro uprights, counters & blast freezers. Call 0203 952 4822.";
                } else if (name.Contains("foster-fridge") || name == "foster") {
                    newTitle = "Foster Fridge Repair London | 24/7 Commercial Catering Engineers";
                    newDesc = "24/7 emergency Foster commercial fridge repair in London. Same-day F-Gas engineers for Foster EcoPro cabinets, prep counters & chillers. Call 0203 952 4822.";
                } else if (name.Contains("true-fridge")) {
                    newTitle = "True Commercial Fridge Repair London | 24/7 Same-Day Engineers";
                    newDesc = "24/7 emergency True commercial fridge & freezer repair in London. Same-day F-Gas engineers for True prep tables, undercounters & display chillers. Call 0203 952 4822.";
                } else if (name.Contains("polar-fridge")) {
                    newTitle = "Polar Commercial Fridge Repair London | 24/7 Same-Day Engineers";
                    newDesc = "24/7 emergency Polar commercial fridge & freezer repair in London. Same-day F-Gas engineers for Polar display fridges, prep counters & uprights. Call 0203 952 4822.";
                } else if (name.Contains("gram-fridge")) {
                    newTitle = "Gram Commercial Fridge Repair London | 24/7 Same-Day Engineers";
                    newDesc = "24/7 emergency Gram commercial fridge & freezer repair in London. Same-day F-Gas engineers for Gram Compact & Superior kitchen cabinets. Call 0203 952 4822.";
                } else if (name.Contains("refrigeration-brands")) {
                    newTitle = "Commercial Refrigeration Brands Repaired London | 24/7 F-Gas Engineers";
                    newDesc = "24/7 repair across all commercial refrigeration brands in London: Williams, Foster, True, Polar, Gram, Hoshizaki, Scotsman, Liebherr & Ice-O-Matic. Call 0203 952 4822.";
                } else if (name == "commercial-fridge-repair-london") {
                    newTitle = "Commercial Fridge Repair London | 24/7 Emergency Same-Day Engineers";
                    newDesc = "Emergency commercial fridge repair in London. 60\u201390 Min Target Response, Fixed-Price Diagnosis, F-Gas Certified engineers for kitchens & shops. Call 0203 952 4822.";
                } else if (name == "fridge-repair-london") {
                    newTitle = "Fridge Repair London | 24/7 Commercial Refrigeration & Fridge Service";
                    newDesc = "Same-day fridge repair in London. 60\u201390 Min Target Response, Fixed-Price Diagnosis, F-Gas Certified engineers for commercial fridges. Call 0203 952 4822.";
                } else if (name == "commercial-freezer-repair-london") {
                    newTitle = "Commercial Freezer Repair London | 24/7 Emergency Same-Day Engineers";
                    newDesc = "Emergency commercial freezer repair in London. 60\u201390 Min Target Response, Fixed-Price Diagnosis, F-Gas Certified. Walk-in & kitchen freezers. Call 0203 952 4822.";
                } else if (name == "freezer-repair-london") {
                    newTitle = "Freezer Repair London | 24/7 Same-Day Commercial Freezer Repairs";
                    newDesc = "Emergency commercial freezer repair across London. 24/7 F-Gas certified engineers fixing upright, undercounter, display & walk-in freezers today. Call 0203 952 4822.";
                } else if (name == "cold-room-repair-london") {
                    newTitle = "Cold Room Repair London | 24/7 Walk-In Chiller & Freezer Room Engineers";
                    newDesc = "24/7 walk-in cold room repair in London. 60\u201390 Min Target Response, Fixed-Price Diagnosis, F-Gas Certified engineers. Call 0203 952 4822.";
                } else if (name.Contains("cold-room")) {
                    newTitle = "Cold Room Repair London | 24/7 Walk-In Chiller & Freezer Room Engineers";
                    newDesc = "24/7 walk-in cold room repair in London. Same-day F-Gas engineers for commercial chiller rooms, freezer rooms, compressor & gas leak repairs. Call 0203 952 4822.";
                } else if (name == "commercial-catering-repair-london") {
                    newTitle = "Commercial Catering Repair London | 24/7 Kitchen Refrigeration Engineers";
                    newDesc = "24/7 emergency commercial catering repair in London. Same-day F-Gas engineers for commercial kitchen fridges, prep counters, blast chillers, cold rooms & ice machines. Call 0203 952 4822.";
                } else if (name == "catering-repair-london" || name.Contains("catering")) {
                    newTitle = "Catering Repair London | 24/7 Commercial Catering Refrigeration Engineers";
                    newDesc = "24/7 commercial catering equipment & kitchen refrigeration repair in London. Same-day engineers for restaurants, takeaways, hotels, pubs & dark kitchens. Call 0203 952 4822.";
                } else if (name == "air-conditioning-repair-london" || name.Contains("air-conditioning")) {
                    newTitle = "Air Conditioning Repair London | 24/7 Commercial AC & F-Gas Engineers";
                    newDesc = "24/7 emergency commercial air conditioning repair in London. Same-day F-Gas certified engineers for split systems, ceiling cassettes, VRV/VRF & cellar AC. Call 0203 952 4822.";
                } else if (name == "ice-machine-repair-london") {
                    newTitle = "Ice Machine Repairs & Service London | 24/7 Commercial Engineers";
                    newDesc = "24/7 ice machine repairs & service in London. Same-day engineers for Hoshizaki, Scotsman & Ice-O-Matic cube, flake & nugget ice makers. Call 0203 952 4822.";
                } else if (name == "ice-cream-machine-repair-london") {
                    newTitle = "Commercial Ice Cream & Soft Serve Machine Repair London | 24/7";
                    newDesc = "24/7 commercial ice cream & soft serve machine repair in London. Same-day engineers for Carpigiani, Taylor & Bravo. Trade sites only. Call 0203 952 4822.";
                } else if (name == "commercial-ice-machine-repair-london") {
                    newTitle = "Commercial Ice Machine Repair London | 24/7 Bar & Kitchen Ice Maker Engineers";
                    newDesc = "24/7 commercial ice machine repair in London for bars, restaurants & hotels. Same-day engineers for cube, flake & nugget ice makers. Call 0203 952 4822.";
                } else if (name == "ice-machine-repair-north-london") {
                    newTitle = "Ice Machine Repair North London | 24/7 Enfield, Barnet & Camden Engineers";
                    newDesc = "24/7 ice machine repair in North London. Same-day engineers covering Enfield, Barnet, Camden, Islington & Haringey ice makers. Call 0203 952 4822.";
                } else if (name == "ice-machine-repairs-london") {
                    newTitle = "Ice Machine Repairs London | 24/7 Commercial Ice Maker Service";
                    newDesc = "24/7 ice machine repairs in London: cube, flake & nugget ice makers fixed same day by F-Gas certified commercial engineers. Call 0203 952 4822.";
                } else if (name.Contains("ice-machine")) {
                    newTitle = "Ice Machine Repair London | 24/7 Hoshizaki, Scotsman & Bar Ice Engineers";
                    newDesc = "24/7 emergency commercial ice machine repair in London. Same-day engineers for Hoshizaki, Scotsman, Ice-O-Matic & Manitowoc cube and flake ice makers. Call 0203 952 4822.";
                } else if (name == "chiller-repair-london" || name.Contains("chiller")) {
                    newTitle = "Chiller Repair London | 24/7 Walk-In, Multideck & Display Chiller Engineers";
                    newDesc = "24/7 commercial chiller repair in London. Fast 60\u201390 min response for walk-in chillers, multideck display chillers, cellar coolers & process chillers. Call 0203 952 4822.";
                } else if (name == "display-fridge-repair-london" || name.Contains("display-fridge")) {
                    newTitle = "Display Fridge Repair London | 24/7 Multideck, Serve-Over & Bottle Coolers";
                    newDesc = "24/7 commercial display fridge repair in London. Same-day F-Gas engineers for supermarket multidecks, deli serve-over counters, patisserie & drinks chillers. Call 0203 952 4822.";
                } else if (name == "prep-fridge-repair-london" || name.Contains("prep-fridge")) {
                    newTitle = "Prep Fridge Repair London | 24/7 Saladette, Pizza & Counter Fridge Engineers";
                    newDesc = "24/7 emergency prep counter & saladette fridge repair in London. Same-day F-Gas engineers for Williams, Foster, True & Polar kitchen counter fridges. Call 0203 952 4822.";
                } else if (name == "walk-in-freezer-repair-london" || name.Contains("walk-in-freezer")) {
                    newTitle = "Walk-In Freezer Repair London | 24/7 Emergency Freezer Room Engineers";
                    newDesc = "24/7 walk-in freezer repair in London. 60\u201390 min response for commercial freezer rooms, defrost faults, compressors & F-Gas leaks. Call 0203 952 4822.";
                }

                if (newTitle != "")
                {
                    if (Regex.IsMatch(html, @"<title>[\s\S]*?</title>", RegexOptions.IgnoreCase))
                        html = Regex.Replace(html, @"<title>[\s\S]*?</title>", "<title>" + newTitle + "</title>", RegexOptions.IgnoreCase);

                    if (Regex.IsMatch(html, @"<meta\s+name=[""']description[""'][^>]*>", RegexOptions.IgnoreCase))
                        html = Regex.Replace(html, @"<meta\s+name=[""']description[""'][^>]*>", "<meta name=\"description\" content=\"" + newDesc + "\">", RegexOptions.IgnoreCase);
                }
            }

            // V4.8: fill-only meta description fallback (about/news) - never overwrites, never leaves an empty tag
            if (fallbackDesc.ContainsKey(name) && !rel.StartsWith("blog/") && !html.Contains("<!-- AUTO-SEO-LOCKED -->"))
            {
                bool hasDesc = Regex.IsMatch(html, "<meta[^>]+name=[\"']description[\"'][^>]*content=[\"']\\s*[^\"'\\s]", RegexOptions.IgnoreCase)
                            || Regex.IsMatch(html, "<meta[^>]+content=[\"']\\s*[^\"'\\s][^>]*name=[\"']description[\"']", RegexOptions.IgnoreCase);
                if (!hasDesc)
                {
                    html = Regex.Replace(html, "<meta[^>]+name=[\"']description[\"'][^>]*>", "", RegexOptions.IgnoreCase);
                    html = new Regex("</title>", RegexOptions.IgnoreCase).Replace(html, "</title>\r\n  <meta name=\"description\" content=\"" + fallbackDesc[name] + "\">", 1);
                }
            }

            // Inject Homepage Blog Hub so Google crawls & ranks all blog guides
            if (rel == "index.html" && !html.Contains("<!-- AUTO-SEO-V4-BLOGHUB -->"))
            {
                string blogHub = "\r\n<!-- AUTO-SEO-V4-BLOGHUB -->\r\n" +
                    "<section style=\"max-width:1100px;margin:30px auto;padding:20px;background:#f8fafc;border-radius:10px;border:1px solid #e2e8f0;\">\r\n" +
                    "  <h2 style=\"font-size:22px;margin-bottom:12px;color:#0f172a;\">Commercial Refrigeration &amp; Cold Room Troubleshooting Guides</h2>\r\n" +
                    "  <div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;font-size:14px;\">\r\n" +
                    "    <a href=\"/blog/commercial-fridge-not-cooling.html\" style=\"color:#0284c7;text-decoration:none;font-weight:600;\">&rarr; Why Your Commercial Fridge Is Not Cooling (Emergency Checklist)</a>\r\n" +
                    "    <a href=\"/blog/commercial-fridge-repair-cost-london.html\" style=\"color:#0284c7;text-decoration:none;font-weight:600;\">&rarr; Commercial Fridge Repair Cost in London (2026 Pricing Guide)</a>\r\n" +
                    "    <a href=\"/blog/cold-room-temperature-fluctuation.html\" style=\"color:#0284c7;text-decoration:none;font-weight:600;\">&rarr; Cold Room Temperature Fluctuation: Causes &amp; Fast Fixes</a>\r\n" +
                    "    <a href=\"/blog/why-commercial-freezer-not-freezing.html\" style=\"color:#0284c7;text-decoration:none;font-weight:600;\">&rarr; Commercial Freezer Not Freezing? Compressor &amp; Defrost Faults</a>\r\n" +
                    "    <a href=\"/blog/f-gas-regulations-commercial.html\" style=\"color:#0284c7;text-decoration:none;font-weight:600;\">&rarr; UK F-Gas Regulations for London Restaurants &amp; Supermarkets</a>\r\n" +
                    "    <a href=\"/blog/prevent-commercial-fridge-breakdown.html\" style=\"color:#0284c7;text-decoration:none;font-weight:600;\">&rarr; How to Prevent Commercial Fridge &amp; Cellar Cooler Breakdowns</a>\r\n" +
                    "  </div>\r\n</section>\r\n";
                if (Regex.IsMatch(html, @"</body>", RegexOptions.IgnoreCase))
                    html = Regex.Replace(html, @"</body>", blogHub + "</body>", RegexOptions.IgnoreCase);
            }

            // Inject Schema in <head>
            if (Regex.IsMatch(html, @"</head>", RegexOptions.IgnoreCase))
                html = Regex.Replace(html, @"\s*</head>", (rel == "index.html" ? schemaBlockCore : (moneyMeta.ContainsKey(name) ? BuildMoneySchema(name, moneyMeta[name], bizNodeJson, scOpen, scClose) : schemaBlock)) + "</head>", RegexOptions.IgnoreCase);

            // Inject V4 Footer Links before </body>
            if (Regex.IsMatch(html, @"</body>", RegexOptions.IgnoreCase))
                html = Regex.Replace(html, @"\s*</body>", footerBlock + "</body>", RegexOptions.IgnoreCase);

            if (ContentDiffers(orig, html)) { File.WriteAllText(file, html, new UTF8Encoding(false)); updated++; changedFiles.Add(DescribeDiff(rel, orig, html)); }
        }
        catch { }
    }

    // Generate clean sitemap.xml dynamically
    try
    {
        StringBuilder sb = new StringBuilder();
        sb.AppendLine("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        sb.AppendLine("<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">");
        string today = DateTime.UtcNow.ToString("yyyy-MM-dd");
        foreach (string u in sitemapUrls)
        {
            string prio = (u == "https://www.colddirect.co.uk/") ? "1.0" : (u.Contains("-repair-london") ? "0.9" : "0.8");
            sb.AppendLine("  <url><loc>" + u + "</loc><lastmod>" + today + "</lastmod><changefreq>daily</changefreq><priority>" + prio + "</priority></url>");
        }
        sb.AppendLine("</urlset>");
        File.WriteAllText(Path.Combine(root, "sitemap.xml"), sb.ToString(), new UTF8Encoding(false));
    }
    catch { }

    Response.ContentType = "text/plain";
    Response.Write("AUTO-SEO V4.9 RANKING PUSH OK | HTML Updated: " + updated + " | Sitemap URLs: " + sitemapUrls.Count + " | Time: " + DateTime.UtcNow.ToString("o")
        + (changedFiles.Count > 0 ? " | Changed: " + string.Join(" ;; ", changedFiles.ToArray()) : ""));
}

// A deploy (git checkout / FTP of the LF blobs) only changes line endings of the V4 blocks, which the agent writes with CRLF.
// That is not a content change: never rewrite a page (nor count it as "HTML Updated") for a CRLF/LF-only difference.
bool ContentDiffers(string a, string b)
{
    if (a == b) return false;
    return a.Replace("\r\n", "\n") != b.Replace("\r\n", "\n");
}

// where (and how) two versions of a page first differ - shown in the response when a run rewrites a file
string DescribeDiff(string rel, string a, string b)
{
    int n = Math.Min(a.Length, b.Length), i = 0;
    while (i < n && a[i] == b[i]) i++;
    string x = a.Substring(i, Math.Min(48, a.Length - i)).Replace("\r", "\\r").Replace("\n", "\\n");
    string y = b.Substring(i, Math.Min(48, b.Length - i)).Replace("\r", "\\r").Replace("\n", "\\n");
    return rel + "@" + i + " [" + x + "] -> [" + y + "] (len " + a.Length + "->" + b.Length + ")";
}

// constant-time comparison so the key cannot be guessed through response timing
bool KeysEqual(string a, string b)
{
    int diff = a.Length ^ b.Length;
    int n = Math.Max(a.Length, b.Length);
    for (int i = 0; i < n; i++) diff |= (i < a.Length ? a[i] : 0) ^ (i < b.Length ? b[i] : 0);
    return diff == 0;
}

string J(string s) { return s.Replace("\\", "\\\\").Replace("\"", "\\\""); }

string NormUrl(string s) { s = s.ToLowerInvariant().TrimEnd('/'); if (s.EndsWith(".html")) s = s.Substring(0, s.Length - 5); return s; }

string BuildMoneySchema(string slug, string[] m, string bizNodeJson, string scOpen, string scClose)
{
    string url = "https://www.colddirect.co.uk/" + slug + "/";
    StringBuilder sb = new StringBuilder();
    sb.Append("\r\n<!-- AUTO-SEO-V4-SCHEMA -->\r\n" + scOpen + "\r\n{\r\n  \"@context\": \"https://schema.org\",\r\n  \"@graph\": [\r\n");
    sb.Append(bizNodeJson);
    sb.Append(",\r\n    {\r\n      \"@type\": \"Service\",\r\n      \"@id\": \"" + url + "#service\",\r\n      \"name\": \"" + J(m[2]) + "\",\r\n      \"serviceType\": \"" + J(m[3]) + "\",\r\n      \"url\": \"" + url + "\",\r\n      \"provider\": { \"@id\": \"https://www.colddirect.co.uk/#business\" },\r\n      \"areaServed\": [\"London\", \"Greater London\"],\r\n      \"hoursAvailable\": \"Mo-Su 00:00-23:59\",\r\n      \"hasOfferCatalog\": {\r\n        \"@type\": \"OfferCatalog\",\r\n        \"name\": \"" + J(m[2]) + " - keyword variations\",\r\n        \"itemListElement\": [");
    for (int i = 4; i < m.Length; i++)
    {
        if (i > 4) sb.Append(",");
        sb.Append("\r\n          { \"@type\": \"Offer\", \"itemOffered\": { \"@type\": \"Service\", \"name\": \"" + J(m[i]) + "\" } }");
    }
    sb.Append("\r\n        ]\r\n      }\r\n    }\r\n  ]\r\n}\r\n" + scClose + "\r\n");
    return sb.ToString();
}
</script>
