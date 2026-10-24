<%@ Page Language="C#" EnableSessionState="false" ValidateRequest="false" ResponseEncoding="utf-8" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Net" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.Text.RegularExpressions" %>
<%@ Import Namespace="System.Collections.Generic" %>
<script runat="server">
const string MARK = "CD-UK-IP-2026-994821-VOICE-AI";
const string DENY = "UK IP VIOLATION: Commercial License Required from ColdDirect.co.uk";

string Esc(string s)
{
    if (s == null) return "";
    return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "\\r").Replace("\n", "\\n").Replace("\t", "\\t");
}

bool HostOk(string value)
{
    if (string.IsNullOrEmpty(value)) return false;
    try
    {
        Uri u = new Uri(value);
        string host = (u.Host ?? "").ToLowerInvariant();
        string scheme = (u.Scheme ?? "").ToLowerInvariant();
        if (host == "localhost" || host == "127.0.0.1") return true;
        if (scheme != "https") return false;
        return host == "colddirect.co.uk" || host == "www.colddirect.co.uk";
    }
    catch { return false; }
}

string RequestOrigin()
{
    string origin = Request.Headers["Origin"] ?? "";
    if (HostOk(origin)) return origin;
    string referer = "";
    try { referer = Request.Headers["Referer"] ?? ""; } catch { referer = ""; }
    if (HostOk(referer))
    {
        Uri u = new Uri(referer);
        return u.Scheme + "://" + u.Host;
    }
    return "";
}

string JsonField(string json, string key)
{
    Match m = Regex.Match(json ?? "", "\"" + Regex.Escape(key) + "\"\\s*:\\s*\"((?:\\\\.|[^\"])*)\"");
    if (!m.Success) return "";
    try { return Regex.Unescape(m.Groups[1].Value); } catch { return m.Groups[1].Value; }
}

string LoadKey()
{
    try
    {
        string env = Environment.GetEnvironmentVariable("GEMINI_API_KEY") ?? Environment.GetEnvironmentVariable("GOOGLE_API_KEY") ?? "";
        if (!string.IsNullOrEmpty(env)) return env.Trim();
        string file = Server.MapPath("~/App_Data/gemini-voice.key");
        if (File.Exists(file)) return File.ReadAllText(file).Trim();
    }
    catch { }
    return "";
}

string SystemPrompt()
{
    return "You are the Head Engineer at ColdDirect Ltd (colddirect.co.uk), 27 Felixstowe Road, Enfield, London N9 0DX, with 30 years of hands-on commercial refrigeration and catering-equipment experience across London. "
        + "CRITICAL LANGUAGE LOCK - ZERO MIXING: detect the exact language of the customer. English -> 100% warm conversational British English, never any Farsi. Persian -> 100% warm everyday colloquial Tehran spoken Persian, no bookish words. Any other language -> reply only in that language. "
        + "NEVER reply with a brush-off such as 'tell me the make or error code' or 'describe the problem'. ALWAYS answer the exact words the customer used with a specific technical diagnosis. "
        + "Noise/clicking/buzzing: evaporator or condenser fan blade hitting ice, worn fan motor bearings, compressor start relay clicking; tell them to open the door and check if the noise stops (inside evaporator fan), and to call before the fan or compressor seizes. "
        + "Warm/not cooling: blocked condenser coil or filter, failed door gasket, iced evaporator, refrigerant leak or failing compressor. Leaking/water: blocked condensate drain line or overflowing drip tray. Tripping/no power: compressor or fan motor shorting to earth, burned plug or contactor, control board failure. "
        + "If the customer only says they have a problem, give the top 3 causes (condenser blockage causing poor cooling, evaporator fan icing causing noise or warm cabinet, thermostat/sensor or compressor relay failure) and how to check each right now. "
        + "Spoken answer: one short friendly intro ('Hello mate, Head Engineer at ColdDirect here with thirty years of experience'), then IMMEDIATELY the diagnosis and quick checks in natural everyday speech, spell phone numbers and error codes phonetically, suggest calling 07983 759320, and finish by kindly asking for a Like or a 5-star review. "
        + "Commercial refrigeration and catering only. Return STRICT JSON: {\"language\":\"en\",\"languageLabel\":\"English\",\"spoken\":\"...\",\"summary\":\"...\",\"cause\":\"...\",\"checks\":[\"...\",\"...\",\"...\"]}";
}

string[] DetectLang(string text)
{
    string t = text ?? "";
    if (Regex.IsMatch(t, "[\u067E\u0686\u0698\u06AF\u06CC\u06A9]")) return new string[] { "fa", "Persian" };
    if (Regex.IsMatch(t, "[\u0600-\u06FF]")) return new string[] { "ar", "Arabic" };
    if (Regex.IsMatch(t, "[ğşıİĞŞ]")) return new string[] { "tr", "Turkish" };
    if (Regex.IsMatch(t, "[\u0900-\u097F]")) return new string[] { "hi", "Hindi" };
    return new string[] { "en", "English" };
}

bool Has(string q, string pattern)
{
    return Regex.IsMatch(q, pattern, RegexOptions.IgnoreCase);
}

string SpellCode(string letter, string digits)
{
    string[] w = { "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine" };
    StringBuilder sb = new StringBuilder(letter.ToUpperInvariant());
    foreach (char c in digits) sb.Append(" ").Append(w[c - '0']);
    return sb.ToString();
}

string SpellCodeFa(string letter, string digits)
{
    string[] w = { "صفر", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه" };
    string l = letter.ToUpperInvariant();
    string name = l == "E" ? "ای" : l == "F" ? "اف" : l == "P" ? "پی" : l;
    StringBuilder sb = new StringBuilder(name);
    foreach (char c in digits) sb.Append(" ").Append(w[c - '0']);
    return sb.ToString();
}

// Returns {spoken, summary, cause, check1|check2|check3}
string[] Block(string lang, string sym, string a, string code, string codeFa)
{
    bool fa = lang == "fa";
    switch (sym)
    {
        case "noise":
            return fa ? new string[] {
                "خب، گفتی " + a + " سروصدا می‌کنه. نُه بار از ده بار یکی از این سه تاست. یک: پره‌ی فن اواپراتور داخل دستگاه به یخ گیر کرده، که صدای خِرخِر یا تق‌تق می‌ده. دو: بلبرینگ موتور فن خورده شده، که یه وزوز یا غرش یکسره می‌ده. سه: رله‌ی استارت کمپرسور هِی تیک می‌زنه و کمپرسور راه نمی‌افته، که هر چند دقیقه یه تیک می‌شنوی. یه تست ساده: در رو باز کن و گوش بده. اگه با باز شدن در صدا قطع شد، کار فن داخلیه، چون بیشتر فن‌ها با باز شدن در خاموش می‌شن. اگه صدا ادامه داشت، از فن کندانسور یا کمپرسور پشت یا پایین دستگاهه. نذار چند روز همین‌جوری کار کنه، چون فن یا کمپرسور ممکنه بِگیره و کل دستگاه بخوابه.",
                "صدای " + a + " معمولاً از گیر کردن پره‌ی فن اواپراتور به یخ، خراب شدن بلبرینگ موتور فن، یا تیک زدن رله‌ی استارت کمپرسوره.",
                "پره‌ی فن اواپراتور به یخ می‌خوره، بلبرینگ موتور فن خورده شده (وزوز و غرش)، یا رله‌ی استارت کمپرسور خرابه (تیک‌تیک).",
                "در رو باز کن؛ اگه صدا قطع شد، فن اواپراتور داخلیه.|پشت پنل داخلی رو برای یخ دور فن ببین و پشت دستگاه گوش بده ببین تیک کمپرسوره یا نه.|قبل از اینکه فن یا کمپرسور بگیره با 07983 759320 تماس بگیر." }
            : new string[] {
                "Right, so your " + a + " has got noisy. Nine times out of ten that's one of three things. First, the evaporator fan blade inside is catching a build-up of ice, which gives you a scraping or ticking sound. Second, a fan motor bearing is wearing out, which gives a constant hum, buzz or grinding. Third, the compressor start relay is clicking in and out, which you hear as a click every few minutes while the compressor fails to start. Here's a quick check you can do now: open the door and listen. If the noise stops when the door opens, it's the inside evaporator fan, because most fans cut out with the door open. If it carries on, it's the condenser fan or the compressor at the back or underneath. Please don't leave it running like that for days, because a dragging fan or a struggling compressor can seize, and then you lose the whole cabinet.",
                "Noise on a " + a + " usually comes from the evaporator fan hitting ice, worn fan motor bearings, or the compressor start relay clicking.",
                "Evaporator fan blade catching ice, worn fan-motor bearings (hum or grind), or a failing compressor start relay (repeated clicking).",
                "Open the door: if the noise stops, it is the inside evaporator fan.|Check behind the inside back panel for ice around the fan, and listen at the back for the condenser fan or a clicking compressor.|Call 07983 759320 before the fan or compressor seizes." };
        case "warm":
            return fa ? new string[] {
                "حالا اینکه " + a + " خوب سرد نمی‌کنه. مقصرهای همیشگی به ترتیب: اول کندانسور گرفته، همون شبکه‌ی رادیاتوری پشت یا بالا یا پایین دستگاه. وقتی پُر از گردوخاک و چربی آشپزخونه بشه، دستگاه نمی‌تونه گرما رو بیرون بده و دیگه سرد نمی‌کنه. دوم لاستیک در که پاره شده یا شُل شده و هوای گرم میاد تو. سوم اواپراتور داخل یخ زده و هوای سرد نمی‌چرخه. آخری هم که جدی‌تره، نشتی گاز یا کمپرسوری که داره از کار میفته. تست سریع: کندانسور رو با چراغ‌قوه نگاه کن، اگه پر از خاکه دستگاه رو خاموش کن و با برس تمیزش کن. یه تیکه کاغذ لای در بذار و در رو ببند؛ اگه راحت بیرون اومد، لاستیک آب‌بندی نمی‌کنه. دیواره‌ی پشتی داخل رو ببین برفک سنگین داره یا نه. اگه کمپرسور ساکته و داغه، یا یکسره کار می‌کنه و باز سرد نیست، دیگه کار تکنسینه.",
                a + " که سرد نمی‌کنه معمولاً کندانسورش گرفته، لاستیک درش خرابه، اواپراتورش یخ زده، یا مشکل گاز و کمپرسور داره.",
                "کندانسور یا فیلتر هوا پر از خاک و چربی، لاستیک در که آب‌بندی نمی‌کنه، اواپراتور یخ‌زده، یا کمبود گاز و کمپرسور ضعیف.",
                "دستگاه رو خاموش کن و کندانسور و فیلتر هوا رو با برس تمیز کن.|تست کاغذ رو دور تا دور لاستیک در انجام بده.|اگه یکسره کار می‌کنه یا کمپرسور ساکت و داغه، مواد رو جابه‌جا کن و به 07983 759320 زنگ بزن." }
            : new string[] {
                "Now, the " + a + " running warm. The usual suspects, in order: first, a blocked condenser coil, that's the radiator-style grille at the back, top or bottom. Once it's furred up with dust and kitchen grease, the unit can't get rid of heat, so it runs hot and stops cooling. Second, a split or loose door gasket letting warm air in. Third, the evaporator icing up inside so the cold air can't circulate. And last, the serious one, a refrigerant leak or a compressor on its way out. Quick checks: shine a torch on the condenser; if it's thick with dust, switch off and brush it clean. Close the door on a sheet of paper; if it slides out easily, the gasket isn't sealing. Look for heavy frost on the inside back wall. If the compressor is silent and hot, or it runs non-stop and still isn't cold, that's one for an engineer.",
                "A warm " + a + " is usually a blocked condenser, a failed door gasket, an iced-up evaporator, or a refrigerant or compressor fault.",
                "Condenser coil or air filter blocked with dust and grease, door gasket not sealing, evaporator iced up, or low refrigerant / failing compressor.",
                "Switch off and brush the condenser coil and air filter clean.|Do the paper test on the door gasket all the way round.|If it runs non-stop or the compressor is silent and hot, move the stock and call 07983 759320." };
        case "leak":
            return fa ? new string[] {
                "آب ریختن از " + a + " تقریباً همیشه یعنی آب برفک‌زدایی راه در رو نداره. هر بار که دستگاه دیفراست می‌کنه، آب از یه لوله‌ی درین می‌ره تو سینی پایین که خودش بخار می‌شه. اگه این لوله با خرده‌غذا یا یخ بسته بشه، آب تو کابین سرریز می‌کنه و از زیر در می‌زنه بیرون. یا سینی پایین ترک خورده یا پر شده. تست سریع: پایین دیواره‌ی پشتی داخل یه سوراخ کوچیک درین هست؛ اگه دورش آب یا یخ جمع شده، گرفته. می‌تونی آروم با آب ولرم بشوریش. بعد سینی پایین دستگاه رو بکش بیرون ببین پره یا ترک داره.",
                "نشتی آب " + a + " تقریباً همیشه از گرفتگی لوله‌ی درین یا سرریز سینی آبه.",
                "لوله‌ی درین با خرده‌غذا یا یخ گرفته، سینی آب ترک داره یا سرریز کرده، یا هیتر درین فریزر سوخته.",
                "سوراخ درین پایین دیواره‌ی پشتی رو پیدا کن و آروم با آب ولرم بشور.|سینی زیر دستگاه رو برای سرریز یا ترک چک کن.|اگه دوباره یخ زد یا باز آب داد، به 07983 759320 زنگ بزن." }
            : new string[] {
                "Water on the floor from a " + a + " is nearly always the defrost water not getting away. Every time it defrosts, the water runs down a drain line into a drip tray that normally evaporates it. If that drain line gets blocked with food debris or ice, the water overflows inside the cabinet and runs out under the door. Or the drip tray underneath is cracked or overflowing. Quick checks: look at the bottom of the inside back wall for a small drain hole; if there's water or ice sitting around it, it's blocked, and you can gently flush it with warm water. Then pull out the drip tray underneath and see if it's full or cracked.",
                "Leaks on a " + a + " are almost always a blocked condensate drain line or an overflowing drip tray.",
                "Drain line blocked with debris or ice, a cracked or overflowing drip tray, or a failed drain-line heater on freezers.",
                "Find the drain hole at the base of the inside back wall and flush it gently with warm water.|Check the drip tray underneath for overflow or cracks.|If it refreezes or keeps flooding, call 07983 759320." };
        case "trip":
            return fa ? new string[] {
                "اینکه " + a + " برق رو می‌پرونه یا روشن نمی‌شه باید با احتیاط بررسی بشه، اول ایمنی. اگه فیوز یا کلید محافظ جان رو می‌زنه، رایج‌ترین دلیل اینه که کمپرسور یا موتور فن اتصال بدنه داره، معمولاً بعد از اینکه آب رفته توش. بعدش دوشاخه، سیم یا کنتاکتور سوخته. سومی هم برد کنترل یا منبع تغذیه‌ی خراب. تست سریع: دوشاخه رو بکش و دوشاخه و سیم رو برای جای سوختگی یا بوی پلاستیک داغ نگاه کن. یه پریز دیگه امتحان کن. اگه درست همون لحظه‌ای که کمپرسور روشن می‌شه برق می‌پره، به احتمال زیاد خود کمپرسور یا سیم‌کشیشه. لطفاً هی کلید رو بالا نزن، چون هر بار فشار به کمپرسور و سیم‌کشی میاد.",
                a + " که برق رو می‌پرونه یا روشن نمی‌شه معمولاً اتصال بدنه‌ی کمپرسور یا فن، دوشاخه یا کنتاکتور سوخته، یا برد کنترل خراب داره.",
                "اتصال بدنه‌ی کمپرسور یا موتور فن، دوشاخه و سیم یا کنتاکتور سوخته، یا خرابی برد کنترل و منبع تغذیه.",
                "دوشاخه رو بکش و دوشاخه و سیم رو برای سوختگی چک کن.|یه پریز دیگه امتحان کن و ببین درست موقع روشن شدن کمپرسور برق می‌پره یا نه.|دیگه کلید رو بالا نزن و به 07983 759320 زنگ بزن." }
            : new string[] {
                "Tripping the power or not switching on needs a bit of care, so safety first. If the " + a + " trips the RCD or blows the fuse, the most common cause is the compressor or a fan motor shorting to earth, often after water has got into it. Next is a burned plug, flex or contactor. Third is a failed control board or power supply. Quick checks: unplug it and look at the plug and lead for scorch marks or a hot plastic smell. Try it on a different socket. If it trips the moment the compressor kicks in, that's very likely the compressor or its wiring. And please don't keep resetting the breaker, because every trip stresses the compressor and the wiring.",
                "A " + a + " that trips the power or won't switch on is usually a compressor or fan motor shorting to earth, a burned plug or contactor, or a failed control board.",
                "Compressor or fan-motor earth fault, burned plug, flex or contactor, or a control-board / power-supply failure.",
                "Unplug it and check the plug and lead for scorch marks.|Try a different socket and note if it trips the moment the compressor starts.|Stop resetting the breaker and call 07983 759320." };
        case "ice":
            return fa ? new string[] {
                "یخ و برفک سنگین داخل " + a + " یعنی سیکل برفک‌زدایی درست کار نمی‌کنه یا هوای گرم و مرطوب داره میاد تو. یا هیتر، تایمر یا سنسور دیفراست خراب شده، یا لاستیک در هوا می‌ده. یخ رو با چاقو از روی کویل نکَن، این‌جوری کویل سوراخ می‌شه و گاز خالی می‌شه. دستگاه رو خاموش کن، مواد رو جابه‌جا کن، در رو باز بذار تا آب بشه. اگه ظرف یکی دو روز دوباره یخ بست، دیگه قطعاً مشکل دیفراسته.",
                "یخ‌زدگی " + a + " معمولاً از خرابی سیکل دیفراست یا ورود هوای مرطوب از دره.",
                "هیتر، تایمر یا سنسور دیفراست خراب، لاستیک در که هوا می‌ده، یا در که زیاد باز می‌مونه.",
                "یخ رو با چیز تیز نکَن.|دستگاه رو خاموش کن و بذار کامل آب بشه، بعد ببین دوباره یخ می‌زنه یا نه.|اگه دوباره یخ زد با 07983 759320 تماس بگیر." }
            : new string[] {
                "Heavy ice building up inside the " + a + " means the defrost isn't doing its job, or warm, moist air is getting in. Either the defrost heater, timer or probe has failed, or the door gasket is letting air through. Please don't chip the ice off the coil with a knife, that's exactly how coils get punctured and lose their gas. Switch it off, move the stock, leave the door open and let it thaw fully. If it ices up again within a day or two, it's a defrost fault for sure.",
                "Ice build-up in a " + a + " is usually a failed defrost cycle or moist air getting in past the door.",
                "Failed defrost heater, timer or probe, a leaking door gasket, or the door being left open.",
                "Don't chip the ice off with anything sharp.|Switch off, let it thaw fully, then watch whether it ices again within a day or two.|If it ices up again, call 07983 759320." };
        case "noice":
            return fa ? new string[] {
                "اگه یخساز یخ نمی‌ده، اول آب و رسوب و دفع گرما رو چک می‌کنیم، نه اینکه دستگاه رو عوض کنیم. شیر آب باز باشه، فیلتر ورودی نگرفته باشه، سوییچ مخزن گیر نکرده باشه و کندانسور تمیز باشه. اواپراتور رسوب‌گرفته یه لایه یخ نازک و ناهماهنگ می‌زنه و دیگه رهاش نمی‌کنه. اگه فیلتر آب چند ماهه عوض نشده، این خیلی رایجه.",
                "یخ ندادن یخساز معمولاً از آب، رسوب اواپراتور، کندانسور کثیف یا سوییچ مخزنه.",
                "شیر آب بسته، فیلتر ورودی گرفته، رسوب آهک، کندانسور کثیف یا سوییچ مخزن که فکر می‌کنه مخزن پره.",
                "ببین آب به دستگاه می‌رسه و فیلتر نگرفته.|اگه ورقه‌ی یخ نازک و ناهماهنگه و نمی‌افته، رسوبه.|کندانسور رو تمیز کن و اگه درست نشد به 07983 759320 زنگ بزن." }
            : new string[] {
                "If the ice machine isn't making ice, we nearly always start with water, scale and heat, not a new machine. Check the water tap is open, the inlet filter isn't clogged, the bin switch isn't stuck, and the condenser is clean. A scaled-up evaporator freezes a thin, patchy skin of ice and then won't harvest it. If the water filter is months overdue, that's a very common fault in London pubs and restaurants.",
                "No ice usually means water supply, scale on the evaporator, a dirty condenser, or a harvest or bin switch fault.",
                "Closed water tap, blocked inlet filter, limescale, a dirty condenser, or a bin switch that thinks the bin is full.",
                "Confirm water is reaching the machine and the filter isn't blocked.|Look for a thin, patchy ice sheet that won't drop, that's scale.|Clean the condenser, and call 07983 759320 if it still won't harvest." };
        case "code":
            return fa ? new string[] {
                "گفتی دستگاه کد " + codeFa + " نشون می‌ده. روی بیشتر کنترلرهای صنعتی مثل فاستر، ویلیامز، دیکسل، کارل و الیول، این مدل کدها معمولاً یعنی خرابی سنسور یا آلارم دمای بالا. یعنی یا کابین واقعاً گرم شده، یا سنسور شُل شده، یخ زده یا سوخته. اول کندانسور رو تمیز کن، لاستیک در رو چک کن و ببین مواد جلوی دریچه‌ی برگشت هوا رو نگرفته باشه. بعد با یه دماسنج جدا دمای واقعی رو بگیر؛ اگه دما خوبه ولی کد هست، سنسوره.",
                "کد " + code + " روی بیشتر کنترلرها معنیش آلارم دمای بالا یا خرابی سنسوره.",
                "کابین واقعاً گرم شده (کندانسور، لاستیک در، جریان هوا) یا سنسور هوا یا اواپراتور خراب یا شل شده.",
                "کندانسور رو تمیز کن و لاستیک در رو چک کن.|با یه دماسنج جدا دمای واقعی رو بگیر.|اگه دما بالای ۸ درجه است یا کد پاک نمی‌شه، به 07983 759320 زنگ بزن." }
            : new string[] {
                "You mentioned the code " + SpellCode(code.Substring(0, 1), code.Substring(1)) + ". On most commercial controllers, Foster, Williams, Dixell, Carel and Eliwell, a code like that points to either a probe fault or a high-temperature alarm. So either the cabinet really has gone warm, or the sensor is loose, iced up or failed. Start by cleaning the condenser, checking the door gasket, and making sure stock isn't blocking the return air. Then check the real temperature with a separate thermometer. If the temperature is fine but the code is still showing, it's the probe itself.",
                "Code " + code + " on most commercial controllers means a high-temperature alarm or a probe fault.",
                "The cabinet has genuinely warmed up (condenser, gasket, airflow), or the air or evaporator probe is loose, iced or failed.",
                "Clean the condenser and check the door gasket.|Check the real temperature with a separate thermometer.|If it's above 8°C or the code won't clear, call 07983 759320." };
        default:
            return fa ? new string[] {
                "اگه " + a + " اذیتت می‌کنه، این سه تا خرابی رو از همه بیشتر می‌بینم و همین الان می‌تونی چکشون کنی. یک: کندانسور از گردوخاک گرفته و داغ می‌کنه، که باعث می‌شه دستگاه خوب سرد نکنه و پشتش داغ باشه. دستگاه رو خاموش کن و با برس تمیزش کن. دو: فن اواپراتور داخل یخ زده، که یا صدا می‌ده یا کابین گرم می‌شه. در رو باز کن و گوش بده، و دیواره‌ی پشتی داخل رو برای برفک سنگین نگاه کن. سه: ترموستات، سنسور دما یا رله‌ی کمپرسور خراب شده. اگه نمایشگر دمای اشتباه نشون می‌ده، یا هر چند دقیقه یه تیک می‌شنوی ولی کمپرسور روشن نمی‌شه، مقصر همینه.",
                "سه خرابی رایج " + a + ": کندانسور گرفته و داغ، فن اواپراتور یخ‌زده، یا خرابی ترموستات، سنسور یا رله‌ی کمپرسور.",
                "کندانسور گرفته که خنک‌کاری رو ضعیف می‌کنه، فن اواپراتور یخ‌زده که صدا یا گرمی کابین میاره، یا خرابی ترموستات و سنسور و رله‌ی کمپرسور.",
                "دستگاه رو خاموش کن و کندانسور رو با برس تمیز کن.|در رو باز کن و گوش بده، و دیواره‌ی پشتی رو برای برفک ببین.|دمای نمایشگر رو با یه دماسنج جدا مقایسه کن و اگه کمپرسور فقط تیک می‌زنه به 07983 759320 زنگ بزن." }
            : new string[] {
                "If your " + a + " is playing up, here are the three faults I see most often, and you can check all of them right now. Number one, the condenser overheating because it's blocked with dust. That gives you poor cooling and a hot back to the unit, so switch it off and brush it clean. Number two, the evaporator fan icing up inside, which gives you either a noise or a warm cabinet. Open the door and listen, and look for heavy frost on the inside back wall. Number three, the thermostat, the temperature sensor or the compressor relay failing. If the display shows the wrong temperature, or you hear a click every few minutes but the compressor never actually runs, that's your culprit.",
                "The three most common " + a + " breakdowns: a blocked, overheating condenser; an iced-up evaporator fan; or a failed thermostat, sensor or compressor relay.",
                "Condenser blockage causing poor cooling, evaporator fan icing causing noise or a warm cabinet, or thermostat / sensor / compressor-relay failure.",
                "Switch off and brush the condenser clean.|Open the door and listen, and check the inside back wall for heavy frost.|Compare the display with a separate thermometer, and if the compressor only clicks, call 07983 759320." };
    }
}

string FallbackJson(string text)
{
    string[] lang = DetectLang(text);
    string lc = lang[0] == "fa" ? "fa" : "en";
    string label = lc == "fa" ? "Persian" : "English";
    string q = (text ?? "").ToLowerInvariant();

    string a, aFa;
    if (Has(q, "fridge[\\s-]*freezer|freezer[\\s-]*fridge|یخچال\\s*(و\\s*)?فریزر|یخچال‌فریزر")) { a = "fridge freezer"; aFa = "یخچال فریزر"; }
    else if (Has(q, "ice\\s*machine|ice\\s*maker|یخساز|یخ\\s*ساز")) { a = "ice machine"; aFa = "یخساز"; }
    else if (Has(q, "cold\\s*room|walk[\\s-]*in|سردخانه|سردخونه")) { a = "cold room"; aFa = "سردخونه"; }
    else if (Has(q, "cellar|keg|سرداب")) { a = "cellar cooler"; aFa = "خنک‌کننده‌ی سرداب"; }
    else if (Has(q, "freezer|فریزر")) { a = "freezer"; aFa = "فریزر"; }
    else if (Has(q, "fridge|refrigerator|chiller|bottle\\s*cooler|display|یخچال")) { a = "fridge"; aFa = "یخچال"; }
    else { a = "fridge or freezer"; aFa = "یخچال یا فریزر"; }
    string app = lc == "fa" ? aFa : a;

    string code = "", codeFa = "";
    Match cm = Regex.Match(q, "(?<![a-z])([efp])\\s?-?(\\d{1,2})(?!\\d)", RegexOptions.IgnoreCase);
    if (cm.Success) { code = cm.Groups[1].Value.ToUpperInvariant() + cm.Groups[2].Value; codeFa = SpellCodeFa(cm.Groups[1].Value, cm.Groups[2].Value); }

    List<string> syms = new List<string>();
    if (Has(q, "trip|fuse|rcd|breaker|no power|not turn(ing)? on|won'?t (turn|switch) on|doesn'?t (turn|switch) on|not switching on|dead|spark|burn|smoke|برق|فیوز|روشن نمی|قطع می|جرقه|سوخت")) syms.Add("trip");
    if (a == "ice machine" && Has(q, "no ice|not making|won'?t make|isn'?t making|stopp|not working|یخ نمی|کار نمی")) syms.Add("noice");
    if (Has(q, "nois|loud|click|buzz|rattl|hum|grind|squeal|squeak|vibrat|knock|bang|whin|صدا|سروصدا|تق|وزوز|غرش")) syms.Add("noise");
    if (Has(q, "warm|not cool|not cold|isn'?t cold|not freezing|temperatur|temp\\b|hot|defrost(ing|ed)? (food|stock)|thaw|گرم|خنک نمی|سرد نمی|سرما نمی|دما")) syms.Add("warm");
    if (Has(q, "leak|water|puddle|drip|flood|wet|نشت|چکه|آب می|آب داره|آب ریخته")) syms.Add("leak");
    if (Has(q, "ice[\\s-]*up|iced|icing|frost|ice build|ice on|ice block|برفک|یخ زده|یخ بسته")) syms.Add("ice");
    if (code != "" || Has(q, "error|alarm|flashing|code|خطا|ارور|آلارم|کد")) { if (code != "") syms.Add("code"); }
    if (syms.Count == 0) syms.Add("general");
    if (syms.Count > 2) syms = syms.GetRange(0, 2);

    bool fosterE1 = code == "E1" && Has(q, "foster|فاستر");

    string intro = lc == "fa"
        ? "سلام رفیق، سرمهندس کلد دایرکت‌ام، سی ساله تو لندن یخچال و فریزر صنعتی و تجهیزات کترینگ درست می‌کنم. "
        : "Hello mate, Head Engineer at ColdDirect here, with thirty years of experience on commercial fridges, freezers and catering kit across London. ";
    string outro = lc == "fa"
        ? " اگه خواستی همین امروز یه تکنسین بفرستیم، زنگ بزن صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر. اگه کمکت کرد، لطفاً دکمه‌ی لایک رو بزن یا پنج ستاره بده، خیلی کمک می‌کنه کلد دایرکت رشد کنه. قربونت."
        : " If you'd like one of our London engineers out today, give us a ring on oh seven nine eight three, seven five nine, three two oh. And if that helped, I'd really appreciate it if you tap the Like button or leave us a five-star review. It genuinely helps ColdDirect grow. Cheers.";

    StringBuilder spoken = new StringBuilder(intro);
    string summary = "", cause = "";
    List<string> checks = new List<string>();
    for (int i = 0; i < syms.Count; i++)
    {
        string[] b = Block(lc, syms[i], app, code, codeFa);
        if (fosterE1 && syms[i] == "code")
        {
            b[0] = lc == "fa"
                ? "گفتی فاستر کد " + codeFa + " نشون می‌ده. روی کنترلرهای فاستر این معمولاً آلارم دمای بالا یا خرابی سنسوره: یا کابین از محدوده‌ی امن گرم‌تر شده، یا سنسور هوا شل شده، یخ زده یا سوخته. کندانسور بالای دستگاه رو برای گردوخاک ببین، لاستیک در رو چک کن و ببین مواد جلوی برگشت هوا رو نگرفته. اگه دمای مواد از هشت درجه بالاتر رفته، همون روز میایم."
                : "You mentioned a Foster showing " + SpellCode("E", "1") + ". On Foster controllers that's usually a high-temperature or probe alarm: the cabinet has climbed above the safe band, or the air probe is loose, iced or failed. Feel the top condenser for thick dust, check the door gasket is sucking shut, and make sure stock isn't blocking the return air. If food is above eight degrees Celsius, we should be with you the same day.";
        }
        spoken.Append(i > 0 ? " " : "").Append(b[0]);
        if (i == 0) { summary = b[1]; cause = b[2]; }
        else { summary += " " + b[1]; cause += " " + b[2]; }
        string[] cs = b[3].Split('|');
        for (int j = 0; j < cs.Length; j++)
        {
            if (checks.Count >= 5) break;
            if (i > 0 && j == cs.Length - 1) continue;
            checks.Add(cs[j]);
        }
    }
    spoken.Append(outro);

    StringBuilder cj = new StringBuilder("[");
    for (int k = 0; k < checks.Count; k++) cj.Append(k > 0 ? "," : "").Append("\"").Append(Esc(checks[k])).Append("\"");
    cj.Append("]");

    return "{\"ok\":true,\"language\":\"" + lc + "\",\"languageLabel\":\"" + label + "\",\"appliance\":\"" + Esc(a) + "\",\"symptoms\":\"" + Esc(string.Join(",", syms.ToArray())) + "\",\"spoken\":\"" + Esc(spoken.ToString()) + "\",\"summary\":\"" + Esc(summary) + "\",\"cause\":\"" + Esc(cause) + "\",\"checks\":" + cj + ",\"watermark\":\"" + MARK + "\",\"source\":\"vault-engine\"}";
}

string HttpJson(string url, string payload, int timeoutMs)
{
    try
    {
        ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072;
        HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
        req.Method = "POST";
        req.ContentType = "application/json";
        req.Timeout = timeoutMs;
        byte[] bytes = Encoding.UTF8.GetBytes(payload);
        req.ContentLength = bytes.Length;
        using (Stream s = req.GetRequestStream()) s.Write(bytes, 0, bytes.Length);
        using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
        using (StreamReader sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
            return sr.ReadToEnd();
    }
    catch (WebException ex)
    {
        try
        {
            if (ex.Response != null)
            {
                using (StreamReader sr = new StreamReader(ex.Response.GetResponseStream(), Encoding.UTF8))
                    return sr.ReadToEnd();
            }
        }
        catch { }
        return "";
    }
}

string ExtractText(string gemini)
{
    Match m = Regex.Match(gemini ?? "", "\"text\"\\s*:\\s*\"((?:\\\\.|[^\"])*)\"");
    if (!m.Success) return "";
    try { return Regex.Unescape(m.Groups[1].Value); } catch { return ""; }
}

string ParseModelJson(string text)
{
    if (string.IsNullOrEmpty(text)) return null;
    Match m = Regex.Match(text, "\\{[\\s\\S]*\\}");
    if (!m.Success) return null;
    string block = m.Value;
    if (block.IndexOf("\"spoken\"") < 0) return null;
    if (Regex.IsMatch(block, "describe the (make|problem)|tell me (the|your) (make|problem)|let me know (the|your) problem", RegexOptions.IgnoreCase)) return null;
    if (block.IndexOf("\"watermark\"") < 0)
        block = block.TrimEnd().TrimEnd('}') + ",\"watermark\":\"" + MARK + "\",\"source\":\"gemini\"}";
    return block;
}

string GeminiDiagnose(string key, string text)
{
    string prompt = Esc(SystemPrompt());
    string user = Esc(text);
    string body = "{\"systemInstruction\":{\"parts\":[{\"text\":\"" + prompt + "\"}]},\"contents\":[{\"role\":\"user\",\"parts\":[{\"text\":\"" + user + "\"}]}],\"generationConfig\":{\"temperature\":0.35,\"responseMimeType\":\"application/json\"}}";
    string[] models = new string[] { "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite" };
    foreach (string model in models)
    {
        string url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + Uri.EscapeDataString(key);
        string raw = HttpJson(url, body, 28000);
        string parsed = ParseModelJson(ExtractText(raw));
        if (!string.IsNullOrEmpty(parsed)) return parsed;
    }
    return null;
}

protected void Page_Load(object sender, EventArgs e)
{
    Response.TrySkipIisCustomErrors = true;
    Response.ContentEncoding = Encoding.UTF8;
    Response.Cache.SetCacheability(HttpCacheability.NoCache);
    Response.AddHeader("X-Content-Type-Options", "nosniff");
    Response.AddHeader("X-CD-IP", MARK);

    string origin = RequestOrigin();
    if (origin == "")
    {
        Response.StatusCode = 403;
        Response.ContentType = "text/plain";
        Response.Write(DENY);
        Response.End();
        return;
    }
    Response.AddHeader("Access-Control-Allow-Origin", origin);
    Response.AddHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    Response.AddHeader("Access-Control-Allow-Headers", "Content-Type, X-CD-IP, Accept");
    Response.AddHeader("Vary", "Origin");

    if (Request.HttpMethod == "OPTIONS")
    {
        Response.StatusCode = 204;
        Response.End();
        return;
    }
    if (Request.HttpMethod != "POST")
    {
        Response.StatusCode = 405;
        Response.ContentType = "application/json";
        Response.Write("{\"ok\":false,\"error\":\"POST only\",\"watermark\":\"" + MARK + "\"}");
        Response.End();
        return;
    }

    string rawJson = "";
    using (StreamReader sr = new StreamReader(Request.InputStream, Encoding.UTF8))
        rawJson = sr.ReadToEnd();
    string text = (JsonField(rawJson, "text") ?? "").Trim();
    if (text.Length > 2000) text = text.Substring(0, 2000);
    bool hasAudio = rawJson.IndexOf("\"audio\"") >= 0;
    if (text == "" && !hasAudio)
    {
        Response.StatusCode = 400;
        Response.ContentType = "application/json";
        Response.Write("{\"ok\":false,\"error\":\"Type a fault or speak, then try again.\",\"watermark\":\"" + MARK + "\"}");
        Response.End();
        return;
    }

    string key = LoadKey();
    string result = null;
    if (key != "" && text != "")
    {
        try { result = GeminiDiagnose(key, text); } catch { result = null; }
    }
    if (string.IsNullOrEmpty(result)) result = FallbackJson(text);

    Response.ContentType = "application/json";
    Response.Write(result);
}
</script>
