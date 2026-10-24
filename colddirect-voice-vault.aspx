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
        if (File.Exists(file))
        {
            string k = File.ReadAllText(file).Trim();
            return k.IndexOf("PASTE", StringComparison.OrdinalIgnoreCase) >= 0 ? "" : k;
        }
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
        + "ENGLISH TONE: talk like a warm, down-to-earth London senior refrigeration engineer chatting to a shop or restaurant owner over a cup of tea. Never robotic, formal or textbook. Use contractions and everyday British phrasing (you've got, it's playing up, on the blink, iced right up, packed up, chucked out, dodgy relay, blocked up solid, give it a quick look, pop the door open, don't panic, give us a bell, cheers). "
        + "Spoken answer: open warmly, e.g. 'Alright mate, don't stress! I'm the Head Engineer here at ColdDirect, been fixing commercial fridges and catering kit around London for thirty years, and we'll get this sorted for you.', then IMMEDIATELY the specific diagnosis and one or two hands-on checks, use commas and '...' so the voice breathes naturally, spell phone numbers and error codes as words (zero seven nine eight three, seven five nine, three two zero; E one), and finish with 'if this tip helped you out, smash that Like button or drop us a quick five-star review, cheers!'. Summary, cause and checks use the same friendly tone. Persian replies keep their own warm Tehrani style. "
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
                "if your " + a + "'s making a racket or buzzing away, nine times out of ten the evaporator fan at the back's clipping a bit of ice buildup... or the little start relay on the compressor's clicking away, trying to kick in. If it's more of a steady hum or a grind, that's usually a fan motor bearing on its way out. Here's a quick one for you. Pop the door open for a second... if the noise stops straight away, it's definitely that inside fan hitting ice. If it carries on, it's the fan or the compressor round the back or underneath. Don't leave it running like that for days, mate, a dodgy fan or a struggling compressor can seize up, and then you've lost the whole cabinet.",
                "Noisy " + a + "? Nine times out of ten the evaporator fan's clipping ice, a fan motor bearing's worn out, or the compressor start relay's clicking away trying to kick in.",
                "Evaporator fan clipping ice (scraping or ticking), a worn fan motor bearing (hum or grind), or a dodgy compressor start relay (clicking every few minutes).",
                "Pop the door open for a second. If the noise stops straight away, it's the inside fan hitting ice.|Have a peek at the back wall inside for ice round the fan, and listen round the back for a clicking compressor.|Give us a bell on 07983 759320 before the motor burns out." };
        case "warm":
            return fa ? new string[] {
                "حالا اینکه " + a + " خوب سرد نمی‌کنه. مقصرهای همیشگی به ترتیب: اول کندانسور گرفته، همون شبکه‌ی رادیاتوری پشت یا بالا یا پایین دستگاه. وقتی پُر از گردوخاک و چربی آشپزخونه بشه، دستگاه نمی‌تونه گرما رو بیرون بده و دیگه سرد نمی‌کنه. دوم لاستیک در که پاره شده یا شُل شده و هوای گرم میاد تو. سوم اواپراتور داخل یخ زده و هوای سرد نمی‌چرخه. آخری هم که جدی‌تره، نشتی گاز یا کمپرسوری که داره از کار میفته. تست سریع: کندانسور رو با چراغ‌قوه نگاه کن، اگه پر از خاکه دستگاه رو خاموش کن و با برس تمیزش کن. یه تیکه کاغذ لای در بذار و در رو ببند؛ اگه راحت بیرون اومد، لاستیک آب‌بندی نمی‌کنه. دیواره‌ی پشتی داخل رو ببین برفک سنگین داره یا نه. اگه کمپرسور ساکته و داغه، یا یکسره کار می‌کنه و باز سرد نیست، دیگه کار تکنسینه.",
                a + " که سرد نمی‌کنه معمولاً کندانسورش گرفته، لاستیک درش خرابه، اواپراتورش یخ زده، یا مشکل گاز و کمپرسور داره.",
                "کندانسور یا فیلتر هوا پر از خاک و چربی، لاستیک در که آب‌بندی نمی‌کنه، اواپراتور یخ‌زده، یا کمبود گاز و کمپرسور ضعیف.",
                "دستگاه رو خاموش کن و کندانسور و فیلتر هوا رو با برس تمیز کن.|تست کاغذ رو دور تا دور لاستیک در انجام بده.|اگه یکسره کار می‌کنه یا کمپرسور ساکت و داغه، مواد رو جابه‌جا کن و به 07983 759320 زنگ بزن." }
            : new string[] {
                "if your " + a + "'s gone warm and isn't holding temp, first thing... don't let your stock spoil, get anything important into another fridge. Usually, the condenser coil underneath is choked up with kitchen grease and dust so it can't breathe, or the fan motor's packed up. Have a quick feel down by the grille... if it's baking hot or dead silent, that's your culprit. Switch it off and give that coil a good brush. Next, shut the door on a sheet of paper. If it slides out easy, the door seal's had it and warm air's sneaking in. And have a peek at the back wall inside, if it's iced right up, the cold air can't get round. If the compressor's silent and hot, or it's running non-stop and still not cold, you've probably got a gas leak or a compressor on the blink, and that's one for us.",
                "Warm " + a + "? Usually the condenser's choked up with grease and dust, the fan motor's packed up, the door seal's had it, or there's a gas or compressor problem.",
                "Condenser coil choked with grease and dust, a packed-up condenser fan, a door seal letting warm air in, the evaporator iced right up, or low gas / a compressor on the blink.",
                "Feel down by the grille. Baking hot or dead silent? Switch off and brush the condenser clean.|Shut the door on a sheet of paper all the way round. If it slides out easy, the seal's gone.|If it's running non-stop or the compressor's silent and hot, move your stock and ring 07983 759320." };
        case "leak":
            return fa ? new string[] {
                "آب ریختن از " + a + " تقریباً همیشه یعنی آب برفک‌زدایی راه در رو نداره. هر بار که دستگاه دیفراست می‌کنه، آب از یه لوله‌ی درین می‌ره تو سینی پایین که خودش بخار می‌شه. اگه این لوله با خرده‌غذا یا یخ بسته بشه، آب تو کابین سرریز می‌کنه و از زیر در می‌زنه بیرون. یا سینی پایین ترک خورده یا پر شده. تست سریع: پایین دیواره‌ی پشتی داخل یه سوراخ کوچیک درین هست؛ اگه دورش آب یا یخ جمع شده، گرفته. می‌تونی آروم با آب ولرم بشوریش. بعد سینی پایین دستگاه رو بکش بیرون ببین پره یا ترک داره.",
                "نشتی آب " + a + " تقریباً همیشه از گرفتگی لوله‌ی درین یا سرریز سینی آبه.",
                "لوله‌ی درین با خرده‌غذا یا یخ گرفته، سینی آب ترک داره یا سرریز کرده، یا هیتر درین فریزر سوخته.",
                "سوراخ درین پایین دیواره‌ی پشتی رو پیدا کن و آروم با آب ولرم بشور.|سینی زیر دستگاه رو برای سرریز یا ترک چک کن.|اگه دوباره یخ زد یا باز آب داد، به 07983 759320 زنگ بزن." }
            : new string[] {
                "water on the floor from a " + a + " is nearly always the defrost water not getting away. Every time it defrosts, the water runs down a little drain into a tray underneath, and normally it just evaporates off. But if that drain gets blocked up solid with bits of food or ice, the water backs up inside and comes out under the door. Have a look at the bottom of the back wall inside, there's a small drain hole... if there's water or ice sat round it, it's blocked. Give it a gentle flush with warm water. Then pull out the tray underneath and check it's not full or cracked. And get a towel down in the meantime, nobody wants a slip in the kitchen.",
                "Leaking " + a + "? Nearly always the drain's blocked up solid or the drip tray underneath is overflowing.",
                "Drain line blocked up with food bits or ice, a cracked or overflowing drip tray, or on freezers a drain heater that's packed up.",
                "Find the little drain hole at the bottom of the back wall inside and flush it gently with warm water.|Pull out the tray underneath and check it's not full or cracked.|If it ices up again or keeps flooding, give us a bell on 07983 759320." };
        case "trip":
            return fa ? new string[] {
                "اینکه " + a + " برق رو می‌پرونه یا روشن نمی‌شه باید با احتیاط بررسی بشه، اول ایمنی. اگه فیوز یا کلید محافظ جان رو می‌زنه، رایج‌ترین دلیل اینه که کمپرسور یا موتور فن اتصال بدنه داره، معمولاً بعد از اینکه آب رفته توش. بعدش دوشاخه، سیم یا کنتاکتور سوخته. سومی هم برد کنترل یا منبع تغذیه‌ی خراب. تست سریع: دوشاخه رو بکش و دوشاخه و سیم رو برای جای سوختگی یا بوی پلاستیک داغ نگاه کن. یه پریز دیگه امتحان کن. اگه درست همون لحظه‌ای که کمپرسور روشن می‌شه برق می‌پره، به احتمال زیاد خود کمپرسور یا سیم‌کشیشه. لطفاً هی کلید رو بالا نزن، چون هر بار فشار به کمپرسور و سیم‌کشی میاد.",
                a + " که برق رو می‌پرونه یا روشن نمی‌شه معمولاً اتصال بدنه‌ی کمپرسور یا فن، دوشاخه یا کنتاکتور سوخته، یا برد کنترل خراب داره.",
                "اتصال بدنه‌ی کمپرسور یا موتور فن، دوشاخه و سیم یا کنتاکتور سوخته، یا خرابی برد کنترل و منبع تغذیه.",
                "دوشاخه رو بکش و دوشاخه و سیم رو برای سوختگی چک کن.|یه پریز دیگه امتحان کن و ببین درست موقع روشن شدن کمپرسور برق می‌پره یا نه.|دیگه کلید رو بالا نزن و به 07983 759320 زنگ بزن." }
            : new string[] {
                "if your " + a + " keeps tripping the power or won't switch on at all, safety first, yeah? Nine times out of ten the compressor or a fan motor's shorting to earth, usually after a bit of water's got where it shouldn't. Next up is a burnt plug, a dodgy lead or a knackered contactor... and now and then it's the control board that's packed up. Pull the plug out and give it a quick look. Any scorch marks, or a hot plastic smell, and that's your answer. Try it on another socket. If it trips the second the compressor kicks in, it's almost certainly the compressor or its wiring. And please, don't keep flicking the breaker back on, every trip gives the compressor and the wiring a proper hammering.",
                "Tripping the power or won't switch on? Usually the compressor or a fan motor's shorting to earth, a burnt plug or contactor, or the control board's packed up.",
                "Compressor or fan motor shorting to earth, a burnt plug, dodgy lead or knackered contactor, or a control board / power supply on the blink.",
                "Pull the plug and give the plug and lead a quick look for scorch marks or a hot plastic smell.|Try another socket, and notice if it trips the second the compressor kicks in.|Stop flicking the breaker back on and ring 07983 759320." };
        case "ice":
            return fa ? new string[] {
                "یخ و برفک سنگین داخل " + a + " یعنی سیکل برفک‌زدایی درست کار نمی‌کنه یا هوای گرم و مرطوب داره میاد تو. یا هیتر، تایمر یا سنسور دیفراست خراب شده، یا لاستیک در هوا می‌ده. یخ رو با چاقو از روی کویل نکَن، این‌جوری کویل سوراخ می‌شه و گاز خالی می‌شه. دستگاه رو خاموش کن، مواد رو جابه‌جا کن، در رو باز بذار تا آب بشه. اگه ظرف یکی دو روز دوباره یخ بست، دیگه قطعاً مشکل دیفراسته.",
                "یخ‌زدگی " + a + " معمولاً از خرابی سیکل دیفراست یا ورود هوای مرطوب از دره.",
                "هیتر، تایمر یا سنسور دیفراست خراب، لاستیک در که هوا می‌ده، یا در که زیاد باز می‌مونه.",
                "یخ رو با چیز تیز نکَن.|دستگاه رو خاموش کن و بذار کامل آب بشه، بعد ببین دوباره یخ می‌زنه یا نه.|اگه دوباره یخ زد با 07983 759320 تماس بگیر." }
            : new string[] {
                "if your " + a + "'s iced right up inside, the defrost isn't doing its job, or damp, warm air's sneaking in. Either the defrost heater, timer or probe's on the blink, or the door seal's letting air past. Whatever you do, don't go chipping the ice off with a knife... that's exactly how coils get punctured and lose their gas. Switch it off, move your stock, leave the door open and let it thaw right out. If it ices up again in a day or two, it's a defrost fault, no question.",
                "Iced-up " + a + "? The defrost's on the blink, or damp air's sneaking in past the door seal.",
                "Defrost heater, timer or probe on the blink, a door seal letting air past, or the door getting left open.",
                "Don't chip the ice off with anything sharp, you'll puncture the coil.|Switch off, let it thaw right out, then watch if it ices up again in a day or two.|If it does, ring 07983 759320 and we'll sort the defrost." };
        case "noice":
            return fa ? new string[] {
                "اگه یخساز یخ نمی‌ده، اول آب و رسوب و دفع گرما رو چک می‌کنیم، نه اینکه دستگاه رو عوض کنیم. شیر آب باز باشه، فیلتر ورودی نگرفته باشه، سوییچ مخزن گیر نکرده باشه و کندانسور تمیز باشه. اواپراتور رسوب‌گرفته یه لایه یخ نازک و ناهماهنگ می‌زنه و دیگه رهاش نمی‌کنه. اگه فیلتر آب چند ماهه عوض نشده، این خیلی رایجه.",
                "یخ ندادن یخساز معمولاً از آب، رسوب اواپراتور، کندانسور کثیف یا سوییچ مخزنه.",
                "شیر آب بسته، فیلتر ورودی گرفته، رسوب آهک، کندانسور کثیف یا سوییچ مخزن که فکر می‌کنه مخزن پره.",
                "ببین آب به دستگاه می‌رسه و فیلتر نگرفته.|اگه ورقه‌ی یخ نازک و ناهماهنگه و نمی‌افته، رسوبه.|کندانسور رو تمیز کن و اگه درست نشد به 07983 759320 زنگ بزن." }
            : new string[] {
                "when an ice machine stops dropping cubes, it's almost always a scaled-up water float switch, a blocked spray bar, or the condenser's running way too hot. First, check the water tap's actually on and the inlet filter isn't clogged. Then have a look at the ice sheet... if it's thin and patchy and just won't drop, that's limescale, mate. Give the condenser a clean as well, and make sure the bin switch isn't stuck, thinking the bin's already full. If the water filter's months overdue, that's a classic in London pubs and restaurants.",
                "Ice machine not dropping cubes? Almost always a scaled-up float switch, a blocked spray bar, or a condenser running way too hot.",
                "Scaled-up water float switch, blocked spray bar, limescale on the evaporator, a hot dirty condenser, or a stuck bin switch.",
                "Check the water tap's on and the inlet filter isn't clogged.|Thin, patchy ice sheet that won't drop? That's limescale.|Clean the condenser, and if it still won't drop cubes, ring 07983 759320." };
        case "code":
            return fa ? new string[] {
                "گفتی دستگاه کد " + codeFa + " نشون می‌ده. روی بیشتر کنترلرهای صنعتی مثل فاستر، ویلیامز، دیکسل، کارل و الیول، این مدل کدها معمولاً یعنی خرابی سنسور یا آلارم دمای بالا. یعنی یا کابین واقعاً گرم شده، یا سنسور شُل شده، یخ زده یا سوخته. اول کندانسور رو تمیز کن، لاستیک در رو چک کن و ببین مواد جلوی دریچه‌ی برگشت هوا رو نگرفته باشه. بعد با یه دماسنج جدا دمای واقعی رو بگیر؛ اگه دما خوبه ولی کد هست، سنسوره.",
                "کد " + code + " روی بیشتر کنترلرها معنیش آلارم دمای بالا یا خرابی سنسوره.",
                "کابین واقعاً گرم شده (کندانسور، لاستیک در، جریان هوا) یا سنسور هوا یا اواپراتور خراب یا شل شده.",
                "کندانسور رو تمیز کن و لاستیک در رو چک کن.|با یه دماسنج جدا دمای واقعی رو بگیر.|اگه دما بالای ۸ درجه است یا کد پاک نمی‌شه، به 07983 759320 زنگ بزن." }
            : new string[] {
                "you've got " + SpellCode(code.Substring(0, 1), code.Substring(1)) + " showing, yeah? On most commercial controllers, Foster, Williams, Dixell, Carel, Eliwell, that kind of code means either a probe's playing up, or it's a high-temp alarm. So either the cabinet's genuinely gone warm, or the sensor's come loose, iced up or packed in. Give the condenser a clean, check the door seal, and make sure your stock isn't blocking the air vent at the back. Then pop a separate thermometer in... if the temp's fine but the code's still flashing, it's the probe itself, and that's a quick fix.",
                "Code " + code + "? On most commercial controllers that's a probe playing up or a high-temp alarm.",
                "The cabinet's genuinely gone warm (condenser, door seal, blocked airflow), or the air or evaporator probe has come loose, iced up or packed in.",
                "Give the condenser a clean and check the door seal.|Pop a separate thermometer in and check the real temp.|If it's over 8°C or the code won't clear, ring 07983 759320." };
        default:
            return fa ? new string[] {
                "اگه " + a + " اذیتت می‌کنه، این سه تا خرابی رو از همه بیشتر می‌بینم و همین الان می‌تونی چکشون کنی. یک: کندانسور از گردوخاک گرفته و داغ می‌کنه، که باعث می‌شه دستگاه خوب سرد نکنه و پشتش داغ باشه. دستگاه رو خاموش کن و با برس تمیزش کن. دو: فن اواپراتور داخل یخ زده، که یا صدا می‌ده یا کابین گرم می‌شه. در رو باز کن و گوش بده، و دیواره‌ی پشتی داخل رو برای برفک سنگین نگاه کن. سه: ترموستات، سنسور دما یا رله‌ی کمپرسور خراب شده. اگه نمایشگر دمای اشتباه نشون می‌ده، یا هر چند دقیقه یه تیک می‌شنوی ولی کمپرسور روشن نمی‌شه، مقصر همینه.",
                "سه خرابی رایج " + a + ": کندانسور گرفته و داغ، فن اواپراتور یخ‌زده، یا خرابی ترموستات، سنسور یا رله‌ی کمپرسور.",
                "کندانسور گرفته که خنک‌کاری رو ضعیف می‌کنه، فن اواپراتور یخ‌زده که صدا یا گرمی کابین میاره، یا خرابی ترموستات و سنسور و رله‌ی کمپرسور.",
                "دستگاه رو خاموش کن و کندانسور رو با برس تمیز کن.|در رو باز کن و گوش بده، و دیواره‌ی پشتی رو برای برفک ببین.|دمای نمایشگر رو با یه دماسنج جدا مقایسه کن و اگه کمپرسور فقط تیک می‌زنه به 07983 759320 زنگ بزن." }
            : new string[] {
                "when a " + a + " starts playing up out of nowhere, it usually comes down to three classic things. Number one... the condenser's choked up with dust, so it overheats, the cooling goes weak, and the back of the unit feels hot. Switch it off and give it a good brush. Number two... the evaporator fan inside's iced right up, so you get a racket or a warm cabinet. Pop the door open, have a listen, and look for heavy frost on the back wall. Number three... a dodgy thermostat, temperature probe or compressor relay. If the display's showing the wrong temp, or you hear a click every few minutes but the compressor never kicks in, that's your culprit.",
                "Three classic " + a + " faults: a condenser choked up with dust, an evaporator fan iced right up, or a dodgy thermostat, probe or compressor relay.",
                "Choked-up condenser giving weak cooling, an iced-up evaporator fan giving a racket or a warm cabinet, or a dodgy thermostat, probe or compressor relay.",
                "Switch off and give the condenser a good brush.|Pop the door open, have a listen, and look for heavy frost on the back wall.|Check the display against a separate thermometer, and if the compressor just clicks, ring 07983 759320." };
    }
}

string EnIntro(string sym)
{
    switch (sym)
    {
        case "noise": return "Alright mate, don't panic! Head Engineer at ColdDirect here, thirty years on the tools. ";
        case "warm": return "Alright mate, Head Engineer at ColdDirect here, with thirty years in the game. ";
        case "noice": return "Alright mate, don't worry! Head Engineer at ColdDirect here, thirty years fixing catering kit. ";
        case "code": return "Alright mate, easy one here! Head Engineer at ColdDirect, thirty years on the tools. ";
        case "ice": return "Alright mate, don't panic! Head Engineer at ColdDirect here, thirty years on the tools. ";
        case "general": return "Alright mate, you're in safe hands! I'm the Head Engineer at ColdDirect, with thirty years fixing commercial cooling across London. ";
        default: return "Alright mate, don't stress! I'm the Head Engineer here at ColdDirect... been fixing commercial fridges and catering kit around London for thirty years, and we'll get this sorted for you. ";
    }
}

string EnLead(string sym)
{
    if (sym == "general") return "Tell you what, ";
    if (sym == "leak" || sym == "trip") return "Right, ";
    return "Look, ";
}

string EnUrgency(string sym)
{
    switch (sym)
    {
        case "noise": return "before the motor burns out";
        case "warm": return "before your stock spoils";
        case "leak": return "before it turns into a proper flood";
        case "trip": return "and we'll get it safe and running again";
        case "ice": return "before that ice chokes the coil";
        case "noice": return "and we'll get those cubes dropping again";
        case "code": return "and we'll get that code cleared";
        default: return "and we'll get it sorted for you";
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

    string first = syms[0];
    string intro = lc == "fa"
        ? "سلام رفیق، سرمهندس کلد دایرکت‌ام، سی ساله تو لندن یخچال و فریزر صنعتی و تجهیزات کترینگ درست می‌کنم. "
        : EnIntro(first);
    string outro = lc == "fa"
        ? " اگه خواستی همین امروز یه تکنسین بفرستیم، زنگ بزن صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر. اگه کمکت کرد، لطفاً دکمه‌ی لایک رو بزن یا پنج ستاره بده، خیلی کمک می‌کنه کلد دایرکت رشد کنه. قربونت."
        : " Give us a bell on zero seven nine eight three, seven five nine, three two zero, " + EnUrgency(first) + "... and if this tip helped you out, smash that Like button or drop us a quick five-star review. Cheers!";

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
                : "that " + SpellCode("E", "1") + " flashing on your Foster controller just means the cabinet air probe has gone open-circuit or come loose... basically, the controller can't read the temperature anymore. Pop the door open and find the little probe up near the evaporator fan. Check it's clipped in properly and the wire isn't chewed, pinched or pulled out. Switch it off at the wall for a minute, then back on, sometimes that's enough to clear it. If it comes straight back, the probe needs swapping, it's a quick job. In the meantime, pop a separate thermometer in and make sure your food's still under eight degrees.";
            if (lc != "fa")
            {
                b[1] = "Foster E1? The cabinet air probe has gone open-circuit or come loose, so the controller can't read the temperature.";
                b[2] = "Cabinet air probe open-circuit, unclipped, or a chewed or pulled-out probe wire.";
                b[3] = "Pop the door open and check the air probe near the evaporator fan is clipped in and the wire's intact.|Switch off at the wall for a minute and back on to see if it clears.|If E1 comes straight back, ring 07983 759320 for a quick probe swap.";
            }
        }
        string piece = b[0];
        if (lc != "fa") piece = (i == 0 ? EnLead(syms[i]) : "And on top of that, ") + piece;
        spoken.Append(i > 0 ? " " : "").Append(piece);
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
        block = AddField(AddField(block, "watermark", "\"" + MARK + "\""), "source", "\"gemini\"");
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

string AddField(string json, string name, string rawValue)
{
    string t = json.TrimEnd();
    if (t.EndsWith("}")) t = t.Substring(0, t.Length - 1);
    return t + ",\"" + name + "\":" + rawValue + "}";
}

string QuotedValueAfter(string raw, string name, int from)
{
    int i = raw.IndexOf("\"" + name + "\"", from, StringComparison.Ordinal);
    if (i < 0) return null;
    int q1 = raw.IndexOf('"', raw.IndexOf(':', i) + 1);
    if (q1 < 0) return null;
    int q2 = raw.IndexOf('"', q1 + 1);
    return q2 < 0 ? null : raw.Substring(q1 + 1, q2 - q1 - 1);
}

byte[] PcmToWav(byte[] pcm, int rate)
{
    using (MemoryStream ms = new MemoryStream(pcm.Length + 44))
    using (BinaryWriter w = new BinaryWriter(ms))
    {
        w.Write(Encoding.ASCII.GetBytes("RIFF")); w.Write(36 + pcm.Length);
        w.Write(Encoding.ASCII.GetBytes("WAVEfmt ")); w.Write(16); w.Write((short)1); w.Write((short)1);
        w.Write(rate); w.Write(rate * 2); w.Write((short)2); w.Write((short)16);
        w.Write(Encoding.ASCII.GetBytes("data")); w.Write(pcm.Length); w.Write(pcm);
        w.Flush();
        return ms.ToArray();
    }
}

// Returns {"mime":"audio/wav","data":"<base64>"} or null.
string GeminiTts(string key, string spoken)
{
    if (string.IsNullOrEmpty(spoken)) return null;
    string line = "Speak as a warm, relaxed, friendly London male engineer chatting to a cafe owner over a cup of tea. Calm, unhurried pace, natural little pauses at commas and dots, never robotic. Read this exactly:\n\n" + spoken;
    string body = "{\"contents\":[{\"role\":\"user\",\"parts\":[{\"text\":\"" + Esc(line) + "\"}]}],\"generationConfig\":{\"responseModalities\":[\"AUDIO\"],\"speechConfig\":{\"voiceConfig\":{\"prebuiltVoiceConfig\":{\"voiceName\":\"Puck\"}}}}}";
    string url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=" + Uri.EscapeDataString(key);
    string raw = HttpJson(url, body, 60000);
    int at = raw.IndexOf("\"inlineData\"", StringComparison.Ordinal);
    if (at < 0) at = raw.IndexOf("\"inline_data\"", StringComparison.Ordinal);
    if (at < 0) return null;
    string mime = QuotedValueAfter(raw, "mimeType", at) ?? QuotedValueAfter(raw, "mime_type", at) ?? "audio/L16;rate=24000";
    string b64 = QuotedValueAfter(raw, "data", at);
    if (string.IsNullOrEmpty(b64)) return null;
    byte[] bin;
    try { bin = Convert.FromBase64String(b64); } catch { return null; }
    if (bin.Length == 0) return null;
    if (mime.IndexOf("wav", StringComparison.OrdinalIgnoreCase) < 0)
    {
        Match r = Regex.Match(mime, "rate=(\\d+)");
        bin = PcmToWav(bin, r.Success ? int.Parse(r.Groups[1].Value) : 24000);
    }
    return "{\"mime\":\"audio/wav\",\"data\":\"" + Convert.ToBase64String(bin) + "\"}";
}

protected void Page_Load(object sender, EventArgs e)
{
    Server.ScriptTimeout = 120;
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

    string voice = "browser-no-key";
    if (key != "")
    {
        string audio = null;
        try { audio = GeminiTts(key, JsonField(result, "spoken")); } catch { audio = null; }
        voice = audio != null ? "Puck" : "browser-tts-failed";
        if (audio != null) result = AddField(result, "audio", audio);
    }
    result = AddField(result, "voice", "\"" + voice + "\"");

    Response.ContentType = "application/json";
    Response.Write(result);
}
</script>
