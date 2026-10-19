<%@ Page Language="C#" Debug="true" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.Text.RegularExpressions" %>
<%@ Import Namespace="System.Collections.Generic" %>
<script runat="server">
    protected void Page_Load(object sender, EventArgs e)
    {
        if (Request.QueryString["key"] != "cd2026")
        {
            Response.StatusCode = 403;
            Response.Write("Access Denied");
            return;
        }

        string rootPath = Server.MapPath("~/");
        string[] files = Directory.GetFiles(rootPath, "*.html", SearchOption.AllDirectories);

        int updated = 0;
        int scanned = 0;
        int skipped = 0;
        List<string> sitemapUrls = new List<string>();

        string masterKeywords = "commercial fridge repair London, commercial fridge repairs, fridge repair London, London fridge repair, commercial freezer repair London, freezer repair London, cold room repair London, walk in cold room repair London, cellar repair London, cellar cooler repair London, beer cellar cooling repair London, commercial catering repair London, catering equipment repair London, cheap fridge repair London, cheap fridge service London, emergency fridge repair service London, 24/7 commercial refrigeration repairs";

        string schemaOpen = "<scr" + "ipt type=\"application/ld+json\">";
        string schemaClose = "</scr" + "ipt>";
        string schemaJson = "\n<!-- AUTO-SEO-V4-SCHEMA -->\n" + schemaOpen + "\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"HVACBusiness\",\n  \"@id\": \"https://www.colddirect.co.uk/#business\",\n  \"name\": \"Cold Direct Commercial Refrigeration, Cold Room, Cellar & Catering Repair London\",\n  \"url\": \"https://www.colddirect.co.uk/\",\n  \"telephone\": \"+442039524822\",\n  \"priceRange\": \"\u00A3\u00A3\",\n  \"address\": {\n    \"@type\": \"PostalAddress\",\n    \"streetAddress\": \"27 Felixstowe Road\",\n    \"addressLocality\": \"Enfield, London\",\n    \"postalCode\": \"N9 0DX\",\n    \"addressCountry\": \"GB\"\n  },\n  \"areaServed\": \"London\"\n}\n" + schemaClose;

        string homepageBlogHub = "\n<!-- AUTO-SEO-V4-BLOGHUB -->\n" +
            "<section class=\"seo-blog-hub\" style=\"max-width:1140px;margin:30px auto;padding:20px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;font-family:sans-serif;\">\n" +
            "  <h2 style=\"font-size:20px;color:#0f172a;margin-bottom:15px;text-align:center;\">London Commercial Refrigeration, Cellar &amp; Catering Repair Guides</h2>\n" +
            "  <div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;font-size:14px;\">\n" +
            "    <div style=\"padding:12px;background:#fff;border-radius:6px;border:1px solid #e2e8f0;\"><strong>1. Commercial Fridge Not Holding 1\u20134\u00B0C:</strong> Dirty condensers, seized evaporator fans &amp; door gasket checks for trade kitchens. <a href=\"/commercial-fridge-repair-london/\">Read Commercial Fridge Guide &rarr;</a></div>\n" +
            "    <div style=\"padding:12px;background:#fff;border-radius:6px;border:1px solid #e2e8f0;\"><strong>2. Walk-In Cold Room Emergency Checklist:</strong> Iced evaporators, roof condensing unit trips &amp; HACCP stock protection. <a href=\"/cold-room-repair-london/\">Read Cold Room Guide &rarr;</a></div>\n" +
            "    <div style=\"padding:12px;background:#fff;border-radius:6px;border:1px solid #e2e8f0;\"><strong>3. Commercial Freezer Climbing Above -18\u00B0C:</strong> Defrost heater diagnostics, controller faults &amp; same-day London recovery. <a href=\"/commercial-freezer-repair-london/\">Read Freezer Guide &rarr;</a></div>\n" +
            "    <div style=\"padding:12px;background:#fff;border-radius:6px;border:1px solid #e2e8f0;\"><strong>4. Pub Beer Cellar Cooler Breakdowns:</strong> Keeping kegs &amp; cellars at 11\u201313\u00B0C across London bars &amp; hospitality venues. <a href=\"/cellar-cooler-repair-london.asp\">Read Cellar Cooling Guide &rarr;</a></div>\n" +
            "    <div style=\"padding:12px;background:#fff;border-radius:6px;border:1px solid #e2e8f0;\"><strong>5. Commercial Catering Fridge &amp; Prep Counters:</strong> Fixing warm saladettes, pass fridges &amp; catering chillers in 60\u2013120 mins. <a href=\"/catering-repair-london/\">Read Catering Repair Guide &rarr;</a></div>\n" +
            "    <div style=\"padding:12px;background:#fff;border-radius:6px;border:1px solid #e2e8f0;\"><strong>6. Cost-Effective &amp; Cheap Fridge Service London:</strong> How board-level component repairs save trade kitchens from full replacements. <a href=\"/fridge-repair-london/\">Read London Fridge Service Guide &rarr;</a></div>\n" +
            "  </div>\n" +
            "</section>";

        string seoTagBlock = "\n<!-- AUTO-SEO-V4-2026 -->\n" +
            "<div class=\"seo-service-tags\" style=\"font-size:12px;color:#666;padding:12px 15px;text-align:center;border-top:1px solid #eee;margin-top:20px;\">\n" +
            "  <strong>24/7 London Commercial Refrigeration, Cellar &amp; Catering Repair Services:</strong>\n" +
            "  <a href=\"/commercial-fridge-repair-london/\" style=\"color:#555;margin:0 6px;\">Commercial Fridge Repair London</a> |\n" +
            "  <a href=\"/commercial-freezer-repair-london/\" style=\"color:#555;margin:0 6px;\">Commercial Freezer Repair London</a> |\n" +
            "  <a href=\"/cold-room-repair-london/\" style=\"color:#555;margin:0 6px;\">Cold Room Repair London</a> |\n" +
            "  <a href=\"/cellar-cooler-repair-london.asp\" style=\"color:#555;margin:0 6px;\">Cellar Repair London</a> |\n" +
            "  <a href=\"/catering-repair-london/\" style=\"color:#555;margin:0 6px;\">Catering Repair London</a> |\n" +
            "  <a href=\"/commercial-catering-repair-london/\" style=\"color:#555;margin:0 6px;\">Commercial Catering Repair London</a> |\n" +
            "  <a href=\"/air-conditioning-repair-london/\" style=\"color:#555;margin:0 6px;\">Air Conditioning Repair London</a> |\n" +
            "  <a href=\"/fridge-repair-london/\" style=\"color:#555;margin:0 6px;\">Fridge Repair London</a> |\n" +
            "  <a href=\"/freezer-repair-london/\" style=\"color:#555;margin:0 6px;\">Freezer Repair London</a>\n" +
            "</div>";

        foreach (string file in files)
        {
            scanned++;
            try
            {
                string relPath = file.Substring(rootPath.Length).Replace("\\", "/");
                string relLower = relPath.ToLowerInvariant();

                if (!relLower.StartsWith("plesk-") && !relLower.Contains("error_docs") && !relLower.Contains("google"))
                {
                    string cleanUrl = "https://www.colddirect.co.uk/" + relPath.Replace("index.html", "");
                    sitemapUrls.Add(cleanUrl);
                }

                string origContent = File.ReadAllText(file, Encoding.UTF8);
                string content = origContent;

                // 1. Always clean UTF-8 encoding glitches and lock tags first (even on existing V4 pages)
                content = content.Replace("<!-- AUTO-SEO-LOCKED -->", "");
                content = content.Replace("â€”", "—").Replace("â€“", "–").Replace("Â°", "°").Replace("â€™", "’").Replace("Â£", "£").Replace("\u00C2\u00A3", "\u00A3").Replace("\u00C2\u00B0", "\u00B0").Replace("\u00E2\u20AC\u201C", "\u2013").Replace("\u00E2\u20AC\u201D", "\u2014").Replace("\u00E2\u20AC\u2122", "\u2019");

                // 2. Always verify & apply exact target Titles and Meta Descriptions
                string newTitle = "";
                string newDesc = "";

                if (relLower.Contains("cellar"))
                {
                    newTitle = "Cellar Repair London | 24/7 Beer Cellar Cooling & Pub Cooler Repairs";
                    newDesc = "24/7 Cellar Repair London & emergency beer cellar cooling service. Fast 60-min pub & bar cellar cooler repairs across London by F-Gas engineers. Call 0203 952 4822!";
                }
                else if (relLower.Contains("air-conditioning") || relLower.Contains("ac-repair"))
                {
                    newTitle = "Air Conditioning Repair London | 24/7 Commercial AC Service & Engineers";
                    newDesc = "24/7 Air Conditioning Repair London & emergency commercial AC service. Fast 60\u201390 min repairs for Daikin, Mitsubishi, VRV/VRF & split AC units across London. Call 0203 952 4822!";
                }
                else if (relLower.Contains("commercial-catering"))
                {
                    newTitle = "Commercial Catering Repair London | 24/7 Kitchen & Catering Fridge Service";
                    newDesc = "24/7 Commercial Catering Repair London for restaurant kitchens, prep tables, saladettes, blast chillers and catering fridges. F-Gas engineers. Call 0203 952 4822!";
                }
                else if (relLower.Contains("catering"))
                {
                    newTitle = "Catering Repair London | 24/7 Emergency Catering Equipment & Fridge Repairs";
                    newDesc = "24/7 Catering Repair London for emergency catering equipment and fridge repairs. Same-day restaurant kitchen call-outs across London. Call 0203 952 4822!";
                }
                else if (relLower.Contains("cold-room"))
                {
                    newTitle = "Cold Room Repair London | 24/7 Walk-In Chiller & Emergency Service";
                    newDesc = "24/7 Walk-In Cold Room Repair London for restaurants, hotels, butchers & supermarkets. Fast 2-hr emergency response by F-Gas engineers. Call 07983 759320!";
                }
                else if (relLower.Contains("commercial-fridge-repair"))
                {
                    newTitle = "Commercial Fridge Repair London | 24/7 Emergency Service & Repairs";
                    newDesc = "24/7 Commercial Fridge Repair London & Emergency Refrigeration Services. Fast 60-min response for restaurants, catering, shops & walk-in fridges. Fixed-rate quotes.";
                }
                else if (relLower.Contains("commercial-freezer-repair"))
                {
                    newTitle = "Commercial Freezer Repair London | 24/7 Emergency Freezer Service & Repairs";
                    newDesc = "24/7 Commercial Freezer Repair London & emergency freezer services. Fast same-day walk-in, display & catering freezer repairs across all London postcodes.";
                }
                else if (relLower.Contains("walk-in-freezer"))
                {
                    newTitle = "Walk-In Freezer Repair London | 24/7 Emergency Frozen Room Engineers";
                    newDesc = "24/7 Walk-In Freezer Repair London. Same-day frozen room, evaporator and condenser repairs for restaurants, hotels and catering sites. Call 0203 952 4822!";
                }
                else if (relLower.Contains("ice-machine"))
                {
                    newTitle = "Ice Machine Repair London | 24/7 Commercial Ice Maker Engineers";
                    newDesc = "24/7 Ice Machine Repair London for Hoshizaki, Scotsman, Ice-O-Matic and Polar commercial ice makers. Same-day cube, flake and nugget repairs. Call 0203 952 4822!";
                }
                else if (relLower.Contains("chiller-repair") && relLower.IndexOf("blast") < 0)
                {
                    newTitle = "Chiller Repair London | 24/7 Commercial & Walk-In Chiller Engineers";
                    newDesc = "24/7 Chiller Repair London for air-cooled, water and process chillers plus walk-in catering chill. F-Gas engineers across London. Call 0203 952 4822!";
                }
                else if (relLower.Contains("display-fridge"))
                {
                    newTitle = "Display Fridge Repair London | 24/7 Multideck & Serve-Over Engineers";
                    newDesc = "24/7 Display Fridge Repair London for multideck, serve-over and glass-door merchandisers in shops and restaurants. Same-day F-Gas repairs. Call 0203 952 4822!";
                }
                else if (relLower.Contains("prep-fridge"))
                {
                    newTitle = "Prep Fridge Repair London | 24/7 Saladette & Prep Counter Engineers";
                    newDesc = "24/7 Prep Fridge Repair London for saladettes, pizza prep counters and gastronorm wells. Same-day commercial kitchen repairs. Call 0203 952 4822!";
                }
                else if (relLower.Contains("freezer-repair"))
                {
                    newTitle = "Freezer Repair London | 24/7 Same-Day Emergency Freezer Service & Repairs";
                    newDesc = "Looking for London Freezer Repair? Fast 24/7 same-day emergency freezer repair service for restaurants, shops & commercial kitchens across London. Call 0203 952 4822!";
                }
                else if (Regex.IsMatch(relLower, @"(^|/)fridge-repair-london"))
                {
                    newTitle = "Fridge Repair & Service London (2-Hr Emergency) | Commercial & Catering";
                    newDesc = "Fast 24/7 London Fridge Repair & cost-effective commercial fridge service. Same-day emergency repairs for restaurants, pubs, cellar coolers & shops across London.";
                }
                else if (relLower == "index.html")
                {
                    newTitle = "Commercial Fridge & Freezer Repair London | Cellar, Cold Room & Catering 24/7";
                    newDesc = "London's #1 Commercial Fridge Repair, Commercial Freezer Repair, Cold Room, Cellar Repair London & Commercial Catering Repair. 24/7 emergency service\u2014call now!";
                }

                if (!string.IsNullOrEmpty(newTitle))
                {
                    if (Regex.IsMatch(content, "<title>.*?</title>", RegexOptions.IgnoreCase | RegexOptions.Singleline))
                    {
                        content = Regex.Replace(content, "<title>.*?</title>", "<title>" + newTitle + "</title>", RegexOptions.IgnoreCase | RegexOptions.Singleline);
                    }

                    string metaDescTag = "<meta name=\"description\" content=\"" + newDesc + "\" />";
                    if (Regex.IsMatch(content, "<meta\\s+name=[\"']description[\"'][^>]*>", RegexOptions.IgnoreCase))
                    {
                        content = Regex.Replace(content, "<meta\\s+name=[\"']description[\"'][^>]*>", metaDescTag, RegexOptions.IgnoreCase);
                    }
                    else if (content.IndexOf("</head>", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        content = Regex.Replace(content, "</head>", metaDescTag + "\n</head>", RegexOptions.IgnoreCase);
                    }
                }

                // 3. Add missing alt attributes to any new images
                content = Regex.Replace(content, "<img(?![^>]*\\balt=)([^>]*)>", "<img alt=\"Commercial Fridge, Freezer, Cold Room & Catering Repair London - Cold Direct\"$1>", RegexOptions.IgnoreCase);

                // 4. Always refresh the V4.3 footer internal-link block (so AC & commercial catering links propagate sitewide)
                if (content.Contains("<!-- AUTO-SEO-V4-2026 -->"))
                {
                    content = Regex.Replace(content, "<!-- AUTO-SEO-V4-2026 -->[\\s\\S]*?</div>", seoTagBlock.TrimStart('\r', '\n'), RegexOptions.IgnoreCase);
                }
                else
                {
                    content = Regex.Replace(content, "<!-- AUTO-SEO-V[23]-2026 -->[\\s\\S]*?</div>", "", RegexOptions.IgnoreCase);
                    content = Regex.Replace(content, "<!-- AUTO-SEO-V3-SCHEMA -->[\\s\\S]*?</scr" + "ipt>", "", RegexOptions.IgnoreCase);

                    string metaKeywordsTag = "<meta name=\"keywords\" content=\"" + masterKeywords + "\" />";
                    if (Regex.IsMatch(content, "<meta\\s+name=[\"']keywords[\"'][^>]*>", RegexOptions.IgnoreCase))
                    {
                        content = Regex.Replace(content, "<meta\\s+name=[\"']keywords[\"'][^>]*>", metaKeywordsTag, RegexOptions.IgnoreCase);
                    }
                    else if (content.IndexOf("</head>", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        content = Regex.Replace(content, "</head>", metaKeywordsTag + "\n</head>", RegexOptions.IgnoreCase);
                    }

                    if (!content.Contains("<!-- AUTO-SEO-V4-SCHEMA -->") && content.IndexOf("</head>", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        content = Regex.Replace(content, "</head>", schemaJson + "\n</head>", RegexOptions.IgnoreCase);
                    }

                    if (relLower == "index.html" && !content.Contains("<!-- AUTO-SEO-V4-BLOGHUB -->") && content.IndexOf("</body>", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        content = Regex.Replace(content, "</body>", homepageBlogHub + "\n</body>", RegexOptions.IgnoreCase);
                    }

                    if (content.IndexOf("</body>", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        content = Regex.Replace(content, "</body>", seoTagBlock + "\n</body>", RegexOptions.IgnoreCase);
                    }
                }

                // 5. Save file only if changes were made (preserves all Cursor CRO Trust Bar & FAQ blocks!)
                if (content != origContent)
                {
                    File.WriteAllText(file, content, Encoding.UTF8);
                    updated++;
                }
            }
            catch (IOException)
            {
                skipped++;
            }
            catch
            {
                skipped++;
            }
        }

        try
        {
            if (!sitemapUrls.Contains("https://www.colddirect.co.uk/cellar-cooler-repair-london.asp"))
                sitemapUrls.Add("https://www.colddirect.co.uk/cellar-cooler-repair-london.asp");
            if (!sitemapUrls.Contains("https://www.colddirect.co.uk/commercial-catering-repair-london/"))
                sitemapUrls.Add("https://www.colddirect.co.uk/commercial-catering-repair-london/");
            if (!sitemapUrls.Contains("https://www.colddirect.co.uk/air-conditioning-repair-london/"))
                sitemapUrls.Add("https://www.colddirect.co.uk/air-conditioning-repair-london/");

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
            sb.AppendLine("<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">");
            string today = DateTime.UtcNow.ToString("yyyy-MM-dd");

            foreach (string url in sitemapUrls)
            {
                string prio = "0.8";
                string uLow = url.ToLowerInvariant();
                if (uLow.Contains("commercial-fridge") || uLow.Contains("freezer-repair") || uLow.Contains("cold-room") || uLow.Contains("cellar") || uLow.Contains("catering") || uLow.Contains("air-conditioning") || uLow.Contains("ac-repair") || uLow.EndsWith("colddirect.co.uk/"))
                {
                    prio = "1.0";
                }

                sb.AppendLine("  <url>");
                sb.AppendLine("    <loc>" + url + "</loc>");
                sb.AppendLine("    <lastmod>" + today + "</lastmod>");
                sb.AppendLine("    <changefreq>daily</changefreq>");
                sb.AppendLine("    <priority>" + prio + "</priority>");
                sb.AppendLine("  </url>");
            }
            sb.AppendLine("</urlset>");
            File.WriteAllText(Path.Combine(rootPath, "sitemap.xml"), sb.ToString(), Encoding.UTF8);
        }
        catch { }

        Response.Write("<h2>AUTO-SEO V4.3 RANKING PUSH OK | Updated: " + updated + " | Scanned: " + scanned + " | Sitemap URLs: " + sitemapUrls.Count + " | Skipped Locked: " + skipped + "</h2>");
    }
</script>
