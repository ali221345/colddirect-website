<%@ Page Language="C#" Debug="true" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.Text.RegularExpressions" %>
<%@ Import Namespace="System.Collections.Generic" %>
<script runat="server">
protected void Page_Load(object sender, EventArgs e)
{
    if (Request.QueryString["key"] != "cd2026") { Response.StatusCode = 403; Response.Write("403"); return; }
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
        "  \"areaServed\": \"London\"\r\n" +
        "}\r\n" + scClose + "\r\n";

    List<string> filesList = new List<string>();
    try { filesList.AddRange(Directory.GetFiles(root, "*.html", SearchOption.TopDirectoryOnly)); } catch { }
    try
    {
        foreach (string dir in Directory.GetDirectories(root, "*", SearchOption.TopDirectoryOnly))
        {
            string dn = Path.GetFileName(dir).ToLowerInvariant();
            if (dn.StartsWith(".") || dn.StartsWith("_") || dn.Contains("backup") || dn.Contains("plesk") || dn.Contains("stat") || dn.Contains("log") || dn.Contains("error") || dn == "colddirect-public-html" || dn == "node_modules" || dn == "cgi-bin" || dn == "app_data") continue;
            try { filesList.AddRange(Directory.GetFiles(dir, "*.html", SearchOption.AllDirectories)); } catch { }
        }
    }
    catch { }

    int updated = 0;
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

            // Upgrade old V4 blocks cleanly
            html = Regex.Replace(html, @"<!-- AUTO-SEO-V[234]-2026 -->[\s\S]*?</div>\s*", "");
            html = Regex.Replace(html, "<!-- AUTO-SEO-V[34]-SCHEMA -->[\\s\\S]*?" + scClose + "\\s*", "");

            if (!html.Contains("<!-- AUTO-SEO-LOCKED -->") && !rel.StartsWith("blog/"))
            {
                string newTitle = "";
                string newDesc = "";

                if (rel == "index.html") {
                    newTitle = "Commercial Fridge & Freezer Repair London | 24/7 Cold Room, Cellar & Catering Engineers";
                    newDesc = "24/7 emergency commercial fridge repair, commercial freezer repair, cold room, beer cellar cooling, commercial catering & air conditioning repair in London. 60\u201390 min response. Call 0203 952 4822.";
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
                    newDesc = "Emergency commercial fridge repair in London. 60\u201390 min response, 24/7 F-Gas engineers for restaurants, supermarkets, pubs & commercial kitchens. Call 0203 952 4822.";
                } else if (name == "fridge-repair-london") {
                    newTitle = "Fridge Repair London | 24/7 Commercial Refrigeration & Fridge Service";
                    newDesc = "Fast same-day commercial fridge repair in London. 24/7 emergency F-Gas engineers for display fridges, prep counters, bar chillers & kitchen cabinets. Call 0203 952 4822.";
                } else if (name == "commercial-freezer-repair-london") {
                    newTitle = "Commercial Freezer Repair London | 24/7 Walk-In & Kitchen Freezer Engineers";
                    newDesc = "24/7 emergency commercial freezer repair in London. Fast 60\u201390 min callout for walk-in freezers, chest freezers, blast freezers & restaurant kitchens. Call 0203 952 4822.";
                } else if (name == "freezer-repair-london") {
                    newTitle = "Freezer Repair London | 24/7 Same-Day Commercial Freezer Repairs";
                    newDesc = "Emergency commercial freezer repair across London. 24/7 F-Gas certified engineers fixing upright, undercounter, display & walk-in freezers today. Call 0203 952 4822.";
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
                } else if (name == "ice-machine-repair-london" || name.Contains("ice-machine")) {
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
                html = Regex.Replace(html, @"</head>", schemaBlock + "</head>", RegexOptions.IgnoreCase);

            // Inject V4 Footer Links before </body>
            if (Regex.IsMatch(html, @"</body>", RegexOptions.IgnoreCase))
                html = Regex.Replace(html, @"</body>", footerBlock + "</body>", RegexOptions.IgnoreCase);

            if (html != orig) { File.WriteAllText(file, html, new UTF8Encoding(false)); updated++; }
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
    Response.Write("AUTO-SEO V4.4 RANKING PUSH OK | HTML Updated: " + updated + " | Sitemap URLs: " + sitemapUrls.Count + " | Time: " + DateTime.UtcNow.ToString("o"));
}
</script>
