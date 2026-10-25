<%@ Page Language="C#" EnableSessionState="false" ValidateRequest="false" ResponseEncoding="utf-8" %>
<%@ Assembly Name="System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Net" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.Text.RegularExpressions" %>
<%@ Import Namespace="System.Collections" %>
<%@ Import Namespace="System.Collections.Generic" %>
<%@ Import Namespace="System.Web.Script.Serialization" %>
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
    return "You are the Senior Engineer at Cold Direct Ltd (colddirect.co.uk), 27 Felixstowe Road, Enfield, London N9 0DX. 30 years of commercial refrigeration in London only. Kind, polite, no slang. "
        + "Return STRICT JSON only with exactly these keys: "
        + "{\"target_language_code\":\"BCP-47 code of the language the reply MUST be in (e.g. fa-IR, tr-TR, fil-PH, en-GB, ar-SA, es-ES). CRITICAL RULE: If the user asks to translate into a specific language (e.g. translate to Turkish / به ترکی بگو) or speaks a language, set target_language_code to THAT requested language and write the ENTIRE response in that language!\",\"transcript\":\"exact customer words in their own script\",\"display_text\":\"The full text shown on screen in target_language_code. MUST include all 3 parts: (1) Greeting as Senior Engineer at Cold Direct, (2) Concise 2-3 sentence technical troubleshooting answer or requested translation, (3) Closing sentence with clean phone numbers 0203 952 4822 and 07983 759320 AND a clear request to click the green Like & 5-Star Review button below.\",\"spoken_text\":\"The exact text to be read out loud by TTS in target_language_code. Same 3 mandatory parts as display_text, EXCEPT phone numbers MUST be written out in natural spoken words in that target language (never raw digits!) so TTS reads them fluently. For Persian (fa-IR), write: درود بر شما. من مهندس ارشد شرکت کُلد دایرِکت هستم و خوشحالم که ما را انتخاب کردید. [پاسخ فنی کوتاه]. برای اعزام فوری تکنسین در لندن، با شماره تلفن صفر دویست و سه، نهصد و پنجاه و دو، چهل و هشت، بیست و دو، و یا موبایل صفر هفت نه هشت سه، هفتصد و پنجاه و نه، سیصد و بیست تماس بگیرید. اگر این راهنمایی برای شما مفید بود، ممنون می‌شویم دکمه سبز لایک و ثبت نظر پنج ستاره را در پایین همین کادر بزنید.\"} "
        + "Never mix English into a non-English reply. Never skip the phones or the Like request, including Tagalog/Filipino, Turkish, Arabic and Spanish. Commercial refrigeration only, London only.";
}

string[] DetectLang(string text)
{
    string t = text ?? "";
    if (Regex.IsMatch(t, "[\u067E\u0686\u0698\u06AF\u06CC\u06A9]")) return new string[] { "fa", "Persian" };
    if (Regex.IsMatch(t, "[\u0600-\u06FF]")) return new string[] { "ar", "Arabic" };
    if (Regex.IsMatch(t, "[\u0900-\u097F]")) return new string[] { "hi", "Hindi" };
    if (Regex.IsMatch(t, "[\u0980-\u09FF]")) return new string[] { "bn", "Bengali" };
    if (Regex.IsMatch(t, "[\u0400-\u04FF]")) return new string[] { "ru", "Russian" };
    if (Regex.IsMatch(t, "[\u4E00-\u9FFF]")) return new string[] { "zh", "Chinese" };
    if (Regex.IsMatch(t, "[\u3040-\u30FF]")) return new string[] { "ja", "Japanese" };
    if (Regex.IsMatch(t, "[\uAC00-\uD7AF]")) return new string[] { "ko", "Korean" };
    if (Regex.IsMatch(t, "[\u0E00-\u0E7F]")) return new string[] { "th", "Thai" };
    if (Regex.IsMatch(t, "[ğşıİĞŞ]")) return new string[] { "tr", "Turkish" };
    if (Regex.IsMatch(t, "[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]")) return new string[] { "pl", "Polish" };
    if (Regex.IsMatch(t, "[ăâîșțĂÂÎȘȚ]")) return new string[] { "ro", "Romanian" };
    if (Regex.IsMatch(t, "\\b(ang|mga|hindi|yung|naman|talaga|kasi|wala|meron|ayaw|gusto|pridyider|kamusta|kaibigan|gumagana|po)\\b", RegexOptions.IgnoreCase))
        return new string[] { "tl", "Tagalog" };
    if (Regex.IsMatch(t, "[ñ¿¡]|\\b(el|la|los|las|una|está|refrigerador)\\b", RegexOptions.IgnoreCase) && Regex.IsMatch(t, "[áéíóúñ¿¡]", RegexOptions.IgnoreCase))
        return new string[] { "es", "Spanish" };
    return new string[] { "en", "English" };
}

string CanonLang(string lang)
{
    lang = (lang ?? "").Trim().ToLowerInvariant().Replace('_', '-');
    if (lang == "" || lang == "und" || lang == "auto") return "";
    if (lang == "fil" || lang.StartsWith("fil-") || lang == "tagalog" || lang.StartsWith("tl-")) return "tl";
    if (lang.StartsWith("pes") || lang.StartsWith("prs") || lang.StartsWith("per") || lang.StartsWith("far") || lang.StartsWith("fa-")) return "fa";
    if (lang.StartsWith("zh")) return "zh";
    if (lang.StartsWith("pt")) return "pt";
    if (lang.Length > 2 && lang[2] == '-') return lang.Substring(0, 2);
    if (lang.Length > 2) return lang.Substring(0, 2);
    return lang;
}

string RequestedLang(string text)
{
    string t = text ?? "";
    if (Regex.IsMatch(t, "t[uü]rk|turkish|به\\s*ترکی|ترکی\\s*بگو|sa\\s+turkish|sa\\s+turko", RegexOptions.IgnoreCase)) return "tr";
    if (Regex.IsMatch(t, "persian|farsi|فارسی|به\\s*فارسی", RegexOptions.IgnoreCase)) return "fa";
    if (Regex.IsMatch(t, "tagalog|filipino|pilipino|تاگالوگ", RegexOptions.IgnoreCase)) return "tl";
    if (Regex.IsMatch(t, "arabic|عربي|عربی|به\\s*عربی", RegexOptions.IgnoreCase)) return "ar";
    if (Regex.IsMatch(t, "spanish|espa[nñ]ol|castellano|اسپانیایی", RegexOptions.IgnoreCase)) return "es";
    if (Regex.IsMatch(t, "\\benglish\\b|انگلیسی|به\\s*انگلیسی", RegexOptions.IgnoreCase)) return "en";
    if (Regex.IsMatch(t, "french|fran[cç]ais|فرانسه", RegexOptions.IgnoreCase)) return "fr";
    if (Regex.IsMatch(t, "\\burdu\\b|اردو", RegexOptions.IgnoreCase)) return "ur";
    if (Regex.IsMatch(t, "hindi|هندی", RegexOptions.IgnoreCase)) return "hi";
    if (Regex.IsMatch(t, "polish|polski|لهستانی", RegexOptions.IgnoreCase)) return "pl";
    return "";
}

bool HasPhones(string s)
{
    return Regex.IsMatch(s ?? "", "759320|952\\s*4822|0203|07983|seven nine eight|s[iı]f[iı]r yedi|صفر هفت|cero siete|zero seven nine", RegexOptions.IgnoreCase);
}

bool HasLike(string s)
{
    return Regex.IsMatch(s ?? "", "like|review|5-star|five.star|لایک|ستاره|be[gğ]eni|y[iı]ld[iı]z|bituin|estrellas|نجمة|إعجاب|bintang", RegexOptions.IgnoreCase);
}

string GreetDisplay(string code)
{
    switch (code)
    {
        case "fa": return "درود، من مهندس ارشد در شرکت کولد دایرکت هستم و خوشحالم که ما را انتخاب کردید. ";
        case "tr": return "Merhaba. Cold Direct'te kıdemli mühendisim ve bizi seçtiğiniz için memnunum. ";
        case "tl": return "Kumusta. Ako ang Senior Engineer sa Cold Direct at natutuwa akong pinili ninyo kami. ";
        case "ar": return "مرحبا. أنا المهندس الأول في كولد دايركت ويسعدني أنكم اخترتمونا. ";
        case "es": return "Hola. Soy el ingeniero sénior de Cold Direct y me alegra que nos hayan elegido. ";
        default: return "Hello. I am the Senior Engineer at Cold Direct. I am glad you chose our company. ";
    }
}

string CloseDisplay(string code)
{
    switch (code)
    {
        case "fa": return " برای اعزام فوری تکنسین در لندن، با شماره 0203 952 4822 یا موبایل 07983 759320 تماس بگیرید. اگر این راهنمایی برای شما مفید بود، لطفاً دکمه سبز لایک و ثبت نظر ۵ ستاره را در پایین همین کادر بزنید.";
        case "tr": return " Londra'da acil teknisyen için 0203 952 4822 veya cep 07983 759320'yi arayın. Bu öneri işinize yaradıysa aşağıdaki yeşil Beğen ve 5 yıldızlı yorum düğmesine tıklayın.";
        case "tl": return " Para sa agarang technician sa London, tawagan ang 0203 952 4822 o mobile 07983 759320. Kung nakatulong ito, paki-click ang berdeng Like at 5-Star Review button sa ibaba.";
        case "ar": return " لإرسال فني فوري في لندن اتصلوا على 0203 952 4822 أو الموبايل 07983 759320. إذا أفادتكم النصيحة، اضغطوا زر الإعجاب الأخضر وتقييم الخمس نجوم في أسفل هذا المربع.";
        case "es": return " Para un técnico urgente en Londres llame al 0203 952 4822 o al móvil 07983 759320. Si esto le ayudó, pulse el botón verde de Like y reseña de 5 estrellas abajo.";
        default: return " For a same-day engineer in London, call 0203 952 4822 or mobile 07983 759320. If this helped, please click the green Like & 5-Star Review button below.";
    }
}

string CloseSpoken(string code)
{
    switch (code)
    {
        case "fa": return " برای اعزام فوری تکنسین در لندن، با شماره تلفن صفر دویست و سه، نهصد و پنجاه و دو، چهل و هشت، بیست و دو، و یا موبایل صفر هفت نه هشت سه، هفتصد و پنجاه و نه، سیصد و بیست تماس بگیرید. اگر این راهنمایی برای شما مفید بود، ممنون می‌شویم دکمه سبز لایک و ثبت نظر پنج ستاره را در پایین همین کادر بزنید.";
        case "tr": return " Londra'da acil teknisyen için sıfır iki sıfır üç, dokuz beş iki, kırk sekiz yirmi iki veya cep sıfır yedi dokuz sekiz üç, yedi yüz elli dokuz, üç yüz yirmi'yi arayın. Bu öneri işinize yaradıysa aşağıdaki yeşil Beğen ve beş yıldızlı yorum düğmesine tıklayın.";
        case "tl": return " Para sa agarang technician sa London, tawagan ang zero two zero three, nine five two, four eight two two, o mobile zero seven nine eight three, seven five nine, three two zero. Kung nakatulong ito, paki-click ang berdeng Like at five-star Review button sa ibaba.";
        case "ar": return " لإرسال فني فوري في لندن اتصلوا على صفر اثنان صفر ثلاثة، تسعة خمسة اثنان، أربعة ثمانية اثنان اثنان أو الموبايل صفر سبعة تسعة ثمانية ثلاثة، سبعة خمسة تسعة، ثلاثة اثنان صفر. إذا أفادتكم النصيحة، اضغطوا زر الإعجاب الأخضر وتقييم الخمس نجوم في أسفل هذا المربع.";
        case "es": return " Para un técnico urgente en Londres llame al cero dos cero tres, nueve cinco dos, cuatro ocho dos dos o al móvil cero siete nueve ocho tres, siete cinco nueve, tres dos cero. Si esto le ayudó, pulse el botón verde de Like y reseña de cinco estrellas abajo.";
        default: return " For a same-day engineer in London, call zero two zero three, nine five two, four eight two two, or mobile zero seven nine eight three, seven five nine, three two zero. If this helped, please click the green Like and five-star review button below.";
    }
}

string EnsureDisplay(string code, string text)
{
    string s = text ?? "";
    if (code == "fa") return WrapPersianDisplay(s);
    if (!Regex.IsMatch(s, "Cold Direct|ColdDirect|کولد دایرکت|کُلد", RegexOptions.IgnoreCase))
        s = GreetDisplay(code) + s.TrimStart();
    if (!HasPhones(s) || !HasLike(s)) s = s.TrimEnd() + CloseDisplay(code);
    return s.Trim();
}

string SpokenOffice(string code)
{
    switch (code)
    {
        case "tr": return "sıfır iki sıfır üç, dokuz beş iki, kırk sekiz yirmi iki";
        case "ar": return "صفر اثنان صفر ثلاثة، تسعة خمسة اثنان، أربعة ثمانية اثنان اثنان";
        case "es": return "cero dos cero tres, nueve cinco dos, cuatro ocho dos dos";
        default: return "zero two zero three, nine five two, four eight two two";
    }
}

string SpokenMobile(string code)
{
    switch (code)
    {
        case "tr": return "sıfır yedi dokuz sekiz üç, yedi yüz elli dokuz, üç yüz yirmi";
        case "ar": return "صفر سبعة تسعة ثمانية ثلاثة، سبعة خمسة تسعة، ثلاثة اثنان صفر";
        case "es": return "cero siete nueve ocho tres, siete cinco nueve, tres dos cero";
        default: return "zero seven nine eight three, seven five nine, three two zero";
    }
}

string EnsureSpoken(string code, string text)
{
    string s = text ?? "";
    if (code == "fa") return PersianAudioText(s);
    s = Regex.Replace(s, "(\\+44\\s*\\(?0?\\)?|0)?\\s*203[\\s-]*952[\\s-]*4822", SpokenOffice(code), RegexOptions.IgnoreCase);
    s = Regex.Replace(s, "(\\+44\\s*\\(?0?\\)?|0)?\\s*7983[\\s-]*759[\\s-]*320", SpokenMobile(code), RegexOptions.IgnoreCase);
    if (!Regex.IsMatch(s, "Cold Direct|ColdDirect|کولد|کُلد", RegexOptions.IgnoreCase))
        s = GreetDisplay(code) + s.TrimStart();
    if (!HasPhones(s) || !HasLike(s)) s = s.TrimEnd() + CloseSpoken(code);
    return Regex.Replace(s, "\\s+", " ").Trim();
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
    string name = l == "E" ? "ئی" : l == "F" ? "اِف" : l == "P" ? "پی" : l;
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
                "شما فرمودید " + a + " صدای غیرعادی می‌دهد. در بیشتر موارد، علت یکی از این سه مورد است. نخست، پره‌ی فن اواپراتور داخل دستگاه به یخ برخورد می‌کند و صدای خش‌خش یا تق‌تق ایجاد می‌شود. دوم، بلبرینگ موتور فن فرسوده شده است و صدای وزوز یا غرش یکنواخت شنیده می‌شود. سوم، رله‌ی استارت کمپرسور مدام عمل می‌کند و کمپرسور روشن نمی‌شود، به همین دلیل هر چند دقیقه یک صدای تیک می‌شنوید. یک آزمایش ساده انجام دهید، در دستگاه را باز کنید و گوش دهید. اگر با باز شدن در صدا قطع شد، مشکل از فن داخلی است، زیرا بیشتر فن‌ها با باز شدن در خاموش می‌شوند. اگر صدا ادامه داشت، منشأ آن فن کندانسور یا کمپرسور در پشت یا پایین دستگاه است. لطفاً اجازه ندهید دستگاه چند روز به همین شکل کار کند، چون ممکن است فن یا کمپرسور از کار بیفتد.",
                "صدای " + a + " معمولاً ناشی از برخورد پره‌ی فن اواپراتور با یخ، فرسودگی بلبرینگ موتور فن، یا عمل کردن مداوم رله‌ی استارت کمپرسور است.",
                "برخورد پره‌ی فن اواپراتور با یخ، فرسودگی بلبرینگ موتور فن، یا خرابی رله‌ی استارت کمپرسور.",
                "در را باز کنید؛ اگر صدا قطع شد، مشکل از فن اواپراتور داخلی است.|دیواره‌ی پشتی داخل را از نظر یخ‌زدگی اطراف فن بررسی کنید و به صدای پشت دستگاه دقت کنید.|پیش از آنکه فن یا کمپرسور آسیب ببیند، با شماره‌ی 07983 759320 تماس بگیرید." }
            : new string[] {
                "if your " + a + "'s making a racket or buzzing away, nine times out of ten the evaporator fan at the back's clipping a bit of ice buildup... or the little start relay on the compressor's clicking away, trying to kick in. If it's more of a steady hum or a grind, that's usually a fan motor bearing on its way out. Here's a quick one for you. Pop the door open for a second... if the noise stops straight away, it's definitely that inside fan hitting ice. If it carries on, it's the fan or the compressor round the back or underneath. Don't leave it running like that for days, mate, a dodgy fan or a struggling compressor can seize up, and then you've lost the whole cabinet.",
                "Noisy " + a + "? Nine times out of ten the evaporator fan's clipping ice, a fan motor bearing's worn out, or the compressor start relay's clicking away trying to kick in.",
                "Evaporator fan clipping ice (scraping or ticking), a worn fan motor bearing (hum or grind), or a dodgy compressor start relay (clicking every few minutes).",
                "Pop the door open for a second. If the noise stops straight away, it's the inside fan hitting ice.|Have a peek at the back wall inside for ice round the fan, and listen round the back for a clicking compressor.|Give us a bell on 07983 759320 before the motor burns out." };
        case "warm":
            return fa ? new string[] {
                "اینکه " + a + " به‌خوبی سرد نمی‌کند، معمولاً یکی از این دلایل را دارد. نخست، کندانسور گرفته است، یعنی همان شبکه‌ی رادیاتوری پشت، بالا یا پایین دستگاه. وقتی این شبکه از گرد و غبار و چربی آشپزخانه پر شود، دستگاه نمی‌تواند گرما را دفع کند. دوم، لاستیک در پاره یا شل شده است و هوای گرم وارد کابین می‌شود. سوم، اواپراتور داخلی یخ زده است و هوای سرد جریان پیدا نمی‌کند. در موارد جدی‌تر نیز، نشتی گاز یا ضعف کمپرسور علت است. یک بررسی سریع انجام دهید، کندانسور را با چراغ‌قوه نگاه کنید. اگر پر از گرد و غبار است، دستگاه را خاموش کنید و با برس تمیزش کنید. سپس یک برگه‌ی کاغذ لای در بگذارید و در را ببندید. اگر کاغذ به‌راحتی بیرون آمد، لاستیک در آب‌بندی نمی‌کند. اگر کمپرسور خاموش و داغ است، یا مدام کار می‌کند و باز هم سرد نمی‌کند، بررسی آن به تکنسین نیاز دارد.",
                a + " که سرد نمی‌کند، معمولاً کندانسور گرفته، لاستیک در معیوب، اواپراتور یخ‌زده، یا مشکل گاز و کمپرسور دارد.",
                "کندانسور یا فیلتر هوای پر از گرد و چربی، لاستیک دری که آب‌بندی نمی‌کند، اواپراتور یخ‌زده، یا کمبود گاز و ضعف کمپرسور.",
                "دستگاه را خاموش کنید و کندانسور و فیلتر هوا را با برس تمیز کنید.|آزمایش کاغذ را در تمام اطراف لاستیک در انجام دهید.|اگر دستگاه مدام کار می‌کند یا کمپرسور خاموش و داغ است، مواد را جابه‌جا کنید و با 07983 759320 تماس بگیرید." }
            : new string[] {
                "if your " + a + "'s gone warm and isn't holding temp, first thing... don't let your stock spoil, get anything important into another fridge. Usually, the condenser coil underneath is choked up with kitchen grease and dust so it can't breathe, or the fan motor's packed up. Have a quick feel down by the grille... if it's baking hot or dead silent, that's your culprit. Switch it off and give that coil a good brush. Next, shut the door on a sheet of paper. If it slides out easy, the door seal's had it and warm air's sneaking in. And have a peek at the back wall inside, if it's iced right up, the cold air can't get round. If the compressor's silent and hot, or it's running non-stop and still not cold, you've probably got a gas leak or a compressor on the blink, and that's one for us.",
                "Warm " + a + "? Usually the condenser's choked up with grease and dust, the fan motor's packed up, the door seal's had it, or there's a gas or compressor problem.",
                "Condenser coil choked with grease and dust, a packed-up condenser fan, a door seal letting warm air in, the evaporator iced right up, or low gas / a compressor on the blink.",
                "Feel down by the grille. Baking hot or dead silent? Switch off and brush the condenser clean.|Shut the door on a sheet of paper all the way round. If it slides out easy, the seal's gone.|If it's running non-stop or the compressor's silent and hot, move your stock and ring 07983 759320." };
        case "leak":
            return fa ? new string[] {
                "نشتی آب از " + a + " تقریباً همیشه به این معناست که آب برفک‌زدایی راه خروج ندارد. هر بار که دستگاه برفک‌زدایی می‌کند، آب از طریق لوله‌ی تخلیه به سینی پایین می‌رود و در آنجا تبخیر می‌شود. اگر این لوله با ذرات غذا یا یخ مسدود شود، آب داخل کابین جمع می‌شود و از زیر در بیرون می‌ریزد. همچنین ممکن است سینی پایین ترک خورده یا پر شده باشد. یک بررسی سریع انجام دهید، در پایین دیواره‌ی پشتی داخل، یک سوراخ کوچک تخلیه وجود دارد. اگر اطراف آن آب یا یخ جمع شده است، یعنی مسدود شده است. آن را به‌آرامی با آب ولرم بشویید. سپس سینی زیر دستگاه را بیرون بکشید و مطمئن شوید پر یا ترک‌خورده نیست.",
                "نشتی آب " + a + " تقریباً همیشه ناشی از گرفتگی لوله‌ی تخلیه یا سرریز سینی آب است.",
                "گرفتگی لوله‌ی تخلیه با ذرات غذا یا یخ، ترک یا سرریز سینی آب، یا سوختن هیتر لوله‌ی تخلیه در فریزر.",
                "سوراخ تخلیه‌ی پایین دیواره‌ی پشتی را پیدا کنید و به‌آرامی با آب ولرم بشویید.|سینی زیر دستگاه را از نظر سرریز یا ترک بررسی کنید.|اگر دوباره یخ زد یا نشتی ادامه داشت، با 07983 759320 تماس بگیرید." }
            : new string[] {
                "water on the floor from a " + a + " is nearly always the defrost water not getting away. Every time it defrosts, the water runs down a little drain into a tray underneath, and normally it just evaporates off. But if that drain gets blocked up solid with bits of food or ice, the water backs up inside and comes out under the door. Have a look at the bottom of the back wall inside, there's a small drain hole... if there's water or ice sat round it, it's blocked. Give it a gentle flush with warm water. Then pull out the tray underneath and check it's not full or cracked. And get a towel down in the meantime, nobody wants a slip in the kitchen.",
                "Leaking " + a + "? Nearly always the drain's blocked up solid or the drip tray underneath is overflowing.",
                "Drain line blocked up with food bits or ice, a cracked or overflowing drip tray, or on freezers a drain heater that's packed up.",
                "Find the little drain hole at the bottom of the back wall inside and flush it gently with warm water.|Pull out the tray underneath and check it's not full or cracked.|If it ices up again or keeps flooding, give us a bell on 07983 759320." };
        case "trip":
            return fa ? new string[] {
                "اینکه " + a + " برق را قطع می‌کند یا روشن نمی‌شود، باید با احتیاط بررسی شود و ایمنی در اولویت است. اگر فیوز یا کلید محافظ جان عمل می‌کند، رایج‌ترین علت اتصال بدنه‌ی کمپرسور یا موتور فن است، که معمولاً پس از نفوذ آب رخ می‌دهد. پس از آن، دوشاخه، کابل یا کنتاکتور سوخته، و در برخی موارد خرابی برد کنترل یا منبع تغذیه علت است. یک بررسی سریع انجام دهید، دوشاخه را از پریز بکشید و دوشاخه و کابل را از نظر سوختگی یا بوی پلاستیک داغ بررسی کنید. دستگاه را به پریز دیگری وصل کنید. اگر درست در لحظه‌ی روشن شدن کمپرسور برق قطع می‌شود، به احتمال زیاد مشکل از خود کمپرسور یا سیم‌کشی آن است. لطفاً کلید را پشت سر هم وصل نکنید، چون هر بار به کمپرسور و سیم‌کشی فشار وارد می‌شود.",
                a + " که برق را قطع می‌کند یا روشن نمی‌شود، معمولاً اتصال بدنه‌ی کمپرسور یا فن، دوشاخه یا کنتاکتور سوخته، یا برد کنترل معیوب دارد.",
                "اتصال بدنه‌ی کمپرسور یا موتور فن، سوختگی دوشاخه، کابل یا کنتاکتور، یا خرابی برد کنترل و منبع تغذیه.",
                "دوشاخه را بکشید و دوشاخه و کابل را از نظر سوختگی بررسی کنید.|پریز دیگری را امتحان کنید و ببینید آیا برق درست هنگام روشن شدن کمپرسور قطع می‌شود.|کلید را دوباره وصل نکنید و با 07983 759320 تماس بگیرید." }
            : new string[] {
                "if your " + a + " keeps tripping the power or won't switch on at all, safety first, yeah? Nine times out of ten the compressor or a fan motor's shorting to earth, usually after a bit of water's got where it shouldn't. Next up is a burnt plug, a dodgy lead or a knackered contactor... and now and then it's the control board that's packed up. Pull the plug out and give it a quick look. Any scorch marks, or a hot plastic smell, and that's your answer. Try it on another socket. If it trips the second the compressor kicks in, it's almost certainly the compressor or its wiring. And please, don't keep flicking the breaker back on, every trip gives the compressor and the wiring a proper hammering.",
                "Tripping the power or won't switch on? Usually the compressor or a fan motor's shorting to earth, a burnt plug or contactor, or the control board's packed up.",
                "Compressor or fan motor shorting to earth, a burnt plug, dodgy lead or knackered contactor, or a control board / power supply on the blink.",
                "Pull the plug and give the plug and lead a quick look for scorch marks or a hot plastic smell.|Try another socket, and notice if it trips the second the compressor kicks in.|Stop flicking the breaker back on and ring 07983 759320." };
        case "ice":
            return fa ? new string[] {
                "یخ و برفک سنگین داخل " + a + " به این معناست که چرخه‌ی برفک‌زدایی به‌درستی کار نمی‌کند، یا هوای گرم و مرطوب وارد دستگاه می‌شود. ممکن است هیتر، تایمر یا سنسور برفک‌زدایی خراب شده باشد، یا لاستیک در هوا را عبور دهد. لطفاً یخ را با چاقو از روی کویل جدا نکنید، چون کویل سوراخ می‌شود و گاز آن تخلیه می‌شود. دستگاه را خاموش کنید، مواد را جابه‌جا کنید و در را باز بگذارید تا یخ کاملاً آب شود. اگر ظرف یکی دو روز دوباره یخ زد، مشکل قطعاً از سیستم برفک‌زدایی است.",
                "یخ‌زدگی " + a + " معمولاً ناشی از خرابی چرخه‌ی برفک‌زدایی یا ورود هوای مرطوب از اطراف در است.",
                "خرابی هیتر، تایمر یا سنسور برفک‌زدایی، لاستیک دری که هوا را عبور می‌دهد، یا باز ماندن طولانی در.",
                "یخ را با وسیله‌ی تیز جدا نکنید.|دستگاه را خاموش کنید تا یخ کاملاً آب شود، سپس ببینید دوباره یخ می‌زند یا نه.|اگر دوباره یخ زد، با 07983 759320 تماس بگیرید." }
            : new string[] {
                "if your " + a + "'s iced right up inside, the defrost isn't doing its job, or damp, warm air's sneaking in. Either the defrost heater, timer or probe's on the blink, or the door seal's letting air past. Whatever you do, don't go chipping the ice off with a knife... that's exactly how coils get punctured and lose their gas. Switch it off, move your stock, leave the door open and let it thaw right out. If it ices up again in a day or two, it's a defrost fault, no question.",
                "Iced-up " + a + "? The defrost's on the blink, or damp air's sneaking in past the door seal.",
                "Defrost heater, timer or probe on the blink, a door seal letting air past, or the door getting left open.",
                "Don't chip the ice off with anything sharp, you'll puncture the coil.|Switch off, let it thaw right out, then watch if it ices up again in a day or two.|If it does, ring 07983 759320 and we'll sort the defrost." };
        case "noice":
            return fa ? new string[] {
                "وقتی یخ‌ساز یخ تولید نمی‌کند، پیش از هر چیز باید آب‌رسانی، رسوب و دفع گرما را بررسی کرد، نه اینکه دستگاه را تعویض کرد. مطمئن شوید شیر آب باز است، فیلتر ورودی مسدود نشده، سوییچ مخزن گیر نکرده و کندانسور تمیز است. اواپراتوری که رسوب گرفته است، لایه‌ی یخ نازک و نامنظمی تشکیل می‌دهد و آن را رها نمی‌کند. اگر فیلتر آب چند ماه است تعویض نشده، این مشکل بسیار رایج است.",
                "تولید نکردن یخ در یخ‌ساز معمولاً به آب‌رسانی، رسوب اواپراتور، کندانسور کثیف یا سوییچ مخزن مربوط است.",
                "بسته بودن شیر آب، گرفتگی فیلتر ورودی، رسوب آهک، کندانسور کثیف، یا سوییچ مخزنی که مخزن را پر تشخیص می‌دهد.",
                "مطمئن شوید آب به دستگاه می‌رسد و فیلتر مسدود نیست.|اگر لایه‌ی یخ نازک و نامنظم است و جدا نمی‌شود، علت رسوب است.|کندانسور را تمیز کنید و اگر مشکل برطرف نشد، با 07983 759320 تماس بگیرید." }
            : new string[] {
                "when an ice machine stops dropping cubes, it's almost always a scaled-up water float switch, a blocked spray bar, or the condenser's running way too hot. First, check the water tap's actually on and the inlet filter isn't clogged. Then have a look at the ice sheet... if it's thin and patchy and just won't drop, that's limescale, mate. Give the condenser a clean as well, and make sure the bin switch isn't stuck, thinking the bin's already full. If the water filter's months overdue, that's a classic in London pubs and restaurants.",
                "Ice machine not dropping cubes? Almost always a scaled-up float switch, a blocked spray bar, or a condenser running way too hot.",
                "Scaled-up water float switch, blocked spray bar, limescale on the evaporator, a hot dirty condenser, or a stuck bin switch.",
                "Check the water tap's on and the inlet filter isn't clogged.|Thin, patchy ice sheet that won't drop? That's limescale.|Clean the condenser, and if it still won't drop cubes, ring 07983 759320." };
        case "code":
            return fa ? new string[] {
                "فرمودید دستگاه کد " + codeFa + " نشان می‌دهد. روی بیشتر کنترلرهای صنعتی، مانند فاستر، ویلیامز، دیکسل، کارل و الیول، این نوع کدها معمولاً به معنای خرابی سنسور یا هشدار دمای بالاست. یعنی یا کابین واقعاً گرم شده است، یا سنسور شل شده، یخ زده یا سوخته است. ابتدا کندانسور را تمیز کنید، لاستیک در را بررسی کنید و مطمئن شوید مواد جلوی دریچه‌ی برگشت هوا را نگرفته‌اند. سپس با یک دماسنج جداگانه دمای واقعی را اندازه بگیرید. اگر دما مناسب است ولی کد همچنان نمایش داده می‌شود، مشکل از سنسور است.",
                "کد " + code + " روی بیشتر کنترلرها به معنای هشدار دمای بالا یا خرابی سنسور است.",
                "گرم شدن واقعی کابین به دلیل کندانسور، لاستیک در یا جریان هوا، یا خرابی و شل شدن سنسور هوا یا اواپراتور.",
                "کندانسور را تمیز کنید و لاستیک در را بررسی کنید.|با یک دماسنج جداگانه دمای واقعی را اندازه بگیرید.|اگر دما بالای ۸ درجه است یا کد پاک نمی‌شود، با 07983 759320 تماس بگیرید." }
            : new string[] {
                "you've got " + SpellCode(code.Substring(0, 1), code.Substring(1)) + " showing, yeah? On most commercial controllers, Foster, Williams, Dixell, Carel, Eliwell, that kind of code means either a probe's playing up, or it's a high-temp alarm. So either the cabinet's genuinely gone warm, or the sensor's come loose, iced up or packed in. Give the condenser a clean, check the door seal, and make sure your stock isn't blocking the air vent at the back. Then pop a separate thermometer in... if the temp's fine but the code's still flashing, it's the probe itself, and that's a quick fix.",
                "Code " + code + "? On most commercial controllers that's a probe playing up or a high-temp alarm.",
                "The cabinet's genuinely gone warm (condenser, door seal, blocked airflow), or the air or evaporator probe has come loose, iced up or packed in.",
                "Give the condenser a clean and check the door seal.|Pop a separate thermometer in and check the real temp.|If it's over 8°C or the code won't clear, ring 07983 759320." };
        default:
            return fa ? new string[] {
                "اگر " + a + " دچار مشکل شده است، این سه خرابی را بیش از همه می‌بینیم و همین حالا می‌توانید بررسی‌شان کنید. نخست، کندانسور از گرد و غبار گرفته و داغ می‌شود، در نتیجه دستگاه به‌خوبی سرد نمی‌کند و پشت آن داغ است. دستگاه را خاموش کنید و با برس تمیزش کنید. دوم، فن اواپراتور داخلی یخ زده است، که باعث صدا یا گرم شدن کابین می‌شود. در را باز کنید، گوش دهید و دیواره‌ی پشتی داخل را از نظر برفک سنگین بررسی کنید. سوم، ترموستات، سنسور دما یا رله‌ی کمپرسور خراب شده است. اگر نمایشگر دمای نادرستی نشان می‌دهد، یا هر چند دقیقه صدای تیک می‌شنوید ولی کمپرسور روشن نمی‌شود، علت همین است.",
                "سه خرابی رایج " + a + ": کندانسور گرفته و داغ، فن اواپراتور یخ‌زده، یا خرابی ترموستات، سنسور یا رله‌ی کمپرسور.",
                "کندانسور گرفته که سرمایش را ضعیف می‌کند، فن اواپراتور یخ‌زده که باعث صدا یا گرم شدن کابین می‌شود، یا خرابی ترموستات، سنسور و رله‌ی کمپرسور.",
                "دستگاه را خاموش کنید و کندانسور را با برس تمیز کنید.|در را باز کنید، گوش دهید و دیواره‌ی پشتی را از نظر برفک بررسی کنید.|دمای نمایشگر را با یک دماسنج جداگانه مقایسه کنید و اگر کمپرسور فقط تیک می‌زند، با 07983 759320 تماس بگیرید." }
            : new string[] {
                "when a " + a + " starts playing up out of nowhere, it usually comes down to three classic things. Number one... the condenser's choked up with dust, so it overheats, the cooling goes weak, and the back of the unit feels hot. Switch it off and give it a good brush. Number two... the evaporator fan inside's iced right up, so you get a racket or a warm cabinet. Pop the door open, have a listen, and look for heavy frost on the back wall. Number three... a dodgy thermostat, temperature probe or compressor relay. If the display's showing the wrong temp, or you hear a click every few minutes but the compressor never kicks in, that's your culprit.",
                "Three classic " + a + " faults: a condenser choked up with dust, an evaporator fan iced right up, or a dodgy thermostat, probe or compressor relay.",
                "Choked-up condenser giving weak cooling, an iced-up evaporator fan giving a racket or a warm cabinet, or a dodgy thermostat, probe or compressor relay.",
                "Switch off and give the condenser a good brush.|Pop the door open, have a listen, and look for heavy frost on the back wall.|Check the display against a separate thermometer, and if the compressor just clicks, ring 07983 759320." };
    }
}

string EnIntro(string sym)
{
    return "Hello. I am the Head Engineer at ColdDirect. I am glad you chose our company. ";
}

string EnLead(string sym)
{
    return "";
}

string EnUrgency(string sym)
{
    return "if you would like an engineer today";
}

string FallbackJson(string text, string hint)
{
    string requested = RequestedLang(text);
    string[] lang = DetectLang(text);
    string lc = requested != "" ? requested : CanonLang(hint);
    if (lc == "") lc = lang[0];
    if (lc == "") lc = "en";
    string label = LabelFor(lc, "");
    string blockLang = lc == "fa" ? "fa" : "en";
    string q = (text ?? "").ToLowerInvariant();

    string a, aFa;
    if (Has(q, "fridge[\\s-]*freezer|freezer[\\s-]*fridge|یخچال\\s*(و\\s*)?فریزر|یخچال‌فریزر")) { a = "fridge freezer"; aFa = "یخچال فریزر"; }
    else if (Has(q, "ice\\s*machine|ice\\s*maker|یخساز|یخ\\s*ساز")) { a = "ice machine"; aFa = "یخساز"; }
    else if (Has(q, "cold\\s*room|walk[\\s-]*in|سردخانه|سردخونه")) { a = "cold room"; aFa = "سردخانه"; }
    else if (Has(q, "cellar|keg|سرداب")) { a = "cellar cooler"; aFa = "خنک‌کننده‌ی سرداب"; }
    else if (Has(q, "freezer|فریزر")) { a = "freezer"; aFa = "فریزر"; }
    else if (Has(q, "fridge|refrigerator|chiller|bottle\\s*cooler|display|یخچال")) { a = "fridge"; aFa = "یخچال"; }
    else { a = "fridge or freezer"; aFa = "یخچال یا فریزر"; }
    string app = blockLang == "fa" ? aFa : a;

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
    string intro = (lc == "en") ? EnIntro(first) : "";
    string outro = "";

    StringBuilder spoken = new StringBuilder(intro);
    string summary = "", cause = "";
    List<string> checks = new List<string>();
    for (int i = 0; i < syms.Count; i++)
    {
        string[] b = Block(blockLang, syms[i], app, code, codeFa);
        if (fosterE1 && syms[i] == "code")
        {
            b[0] = blockLang == "fa"
                ? "فرمودید کنترلر فاستر کد " + codeFa + " نشان می‌دهد. روی کنترلرهای فاستر، این کد یعنی سنسور هوای کابین قطع شده یا از جای خود خارج شده است، و کنترلر دیگر نمی‌تواند دما را بخواند. در را باز کنید و سنسور کوچک نزدیک فن اواپراتور را پیدا کنید. مطمئن شوید در جای خود محکم است و سیم آن بریده، له یا کنده نشده است. دستگاه را یک دقیقه از برق بکشید و دوباره وصل کنید، گاهی همین کار کد را پاک می‌کند. اگر کد بلافاصله برگشت، سنسور باید تعویض شود، که کار سریعی است. در این فاصله، با یک دماسنج جداگانه مطمئن شوید دمای مواد زیر هشت درجه است."
                : "that " + SpellCode("E", "1") + " flashing on your Foster controller just means the cabinet air probe has gone open-circuit or come loose... basically, the controller can't read the temperature anymore. Pop the door open and find the little probe up near the evaporator fan. Check it's clipped in properly and the wire isn't chewed, pinched or pulled out. Switch it off at the wall for a minute, then back on, sometimes that's enough to clear it. If it comes straight back, the probe needs swapping, it's a quick job. In the meantime, pop a separate thermometer in and make sure your food's still under eight degrees.";
            if (blockLang == "fa")
            {
                b[1] = "کد " + code + " روی کنترلر فاستر یعنی سنسور هوای کابین قطع شده یا از جای خود خارج شده است.";
                b[2] = "قطع بودن مدار سنسور هوای کابین، جدا شدن آن از گیره، یا آسیب‌دیدگی سیم سنسور.";
                b[3] = "سنسور نزدیک فن اواپراتور را بررسی کنید که در جای خود باشد و سیمش سالم باشد.|دستگاه را یک دقیقه از برق بکشید و دوباره وصل کنید.|اگر کد دوباره ظاهر شد، برای تعویض سریع سنسور با 07983 759320 تماس بگیرید.";
            }
            else
            {
                b[1] = "Foster E1? The cabinet air probe has gone open-circuit or come loose, so the controller can't read the temperature.";
                b[2] = "Cabinet air probe open-circuit, unclipped, or a chewed or pulled-out probe wire.";
                b[3] = "Pop the door open and check the air probe near the evaporator fan is clipped in and the wire's intact.|Switch off at the wall for a minute and back on to see if it clears.|If E1 comes straight back, ring 07983 759320 for a quick probe swap.";
            }
        }
        string piece = b[0];
        if (blockLang != "fa" && lc == "en") piece = (i == 0 ? EnLead(syms[i]) : "And on top of that, ") + piece;
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
    string spokenOut = EnsureDisplay(lc, spoken.ToString());
    string ttsOut = EnsureSpoken(lc, spoken.ToString());

    StringBuilder cj = new StringBuilder("[");
    for (int k = 0; k < checks.Count; k++) cj.Append(k > 0 ? "," : "").Append("\"").Append(Esc(checks[k])).Append("\"");
    cj.Append("]");

    return "{\"ok\":true,\"language\":\"" + lc + "\",\"languageLabel\":\"" + label + "\",\"appliance\":\"" + Esc(a) + "\",\"symptoms\":\"" + Esc(string.Join(",", syms.ToArray())) + "\",\"spoken\":\"" + Esc(spokenOut) + "\",\"tts_text\":\"" + Esc(ttsOut) + "\",\"summary\":\"" + Esc(summary) + "\",\"cause\":\"" + Esc(cause) + "\",\"checks\":" + cj + ",\"watermark\":\"" + MARK + "\",\"source\":\"vault-engine\"}";
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

JavaScriptSerializer Json()
{
    JavaScriptSerializer s = new JavaScriptSerializer();
    s.MaxJsonLength = int.MaxValue;
    s.RecursionLimit = 64;
    return s;
}

Dictionary<string, object> Obj(object o) { return o as Dictionary<string, object>; }

string Str(Dictionary<string, object> d, params string[] keys)
{
    if (d == null) return "";
    foreach (string k in keys)
    {
        object v;
        if (d.TryGetValue(k, out v) && v != null)
        {
            string s = Convert.ToString(v).Trim();
            if (s != "") return s;
        }
    }
    return "";
}

List<string> StrList(Dictionary<string, object> d, params string[] keys)
{
    List<string> list = new List<string>();
    if (d == null) return list;
    foreach (string k in keys)
    {
        object v;
        if (!d.TryGetValue(k, out v) || v == null) continue;
        IList items = v as IList;
        if (items == null) continue;
        foreach (object it in items)
        {
            string s = Convert.ToString(it ?? "").Trim();
            if (s != "" && list.Count < 5) list.Add(s);
        }
        if (list.Count > 0) break;
    }
    return list;
}

string ModelText(string raw)
{
    try
    {
        Dictionary<string, object> d = Obj(Json().DeserializeObject(raw));
        IList cands = d["candidates"] as IList;
        IList parts = Obj(Obj(cands[0])["content"])["parts"] as IList;
        StringBuilder sb = new StringBuilder();
        foreach (object p in parts)
        {
            Dictionary<string, object> pd = Obj(p);
            if (pd == null) continue;
            object th;
            if (pd.TryGetValue("thought", out th) && th is bool && (bool)th) continue;
            sb.Append(Str(pd, "text"));
        }
        return sb.ToString();
    }
    catch { return ""; }
}

string LabelFor(string code, string name)
{
    if (name != "") return name;
    switch (code)
    {
        case "fa": return "Persian";
        case "en": return "English";
        case "tr": return "Turkish";
        case "ar": return "Arabic";
        case "es": return "Spanish";
        case "tl": return "Tagalog";
        case "fil": return "Tagalog";
        case "hi": return "Hindi";
        case "ur": return "Urdu";
        case "pl": return "Polish";
        case "ro": return "Romanian";
        case "fr": return "French";
        case "ru": return "Russian";
        case "zh": return "Chinese";
        case "pt": return "Portuguese";
        case "bn": return "Bengali";
        case "de": return "German";
        case "it": return "Italian";
        case "ku": return "Kurdish";
        default: return code == "" ? "Detected" : code;
    }
}

const string FA_DISPLAY_OPEN = "درود، من مهندس ارشد در شرکت کولد دایرکت هستم و خوشحالم که ما را انتخاب کردید.";
const string FA_DISPLAY_CLOSE = "برای اعزام فوری تکنسین در لندن، با شماره 0203 952 4822 یا موبایل 07983 759320 تماس بگیرید. اگر این راهنمایی برای شما مفید بود، لطفاً دکمه سبز لایک و ثبت نظر ۵ ستاره را در پایین همین کادر بزنید.";
const string FA_AUDIO_OPEN = "درود بر شما. من مهندس ارشد شرکت کُلد دایرِکت هستم و خوشحالم که ما را انتخاب کردید. ";
const string FA_AUDIO_CLOSE = "برای اعزام فوری تکنسین در لندن، با شماره تلفن صفر دویست و سه، نهصد و پنجاه و دو، چهل و هشت، بیست و دو، و یا موبایل صفر هفت نه هشت سه، هفتصد و پنجاه و نه، سیصد و بیست تماس بگیرید. اگر این راهنمایی برای شما مفید بود، ممنون می‌شویم دکمه سبز لایک و ثبت نظر پنج ستاره را در پایین همین کادر بزنید.";

string TwoFaSentences(string text)
{
    string s = Regex.Replace(text ?? "", "\\s+", " ").Trim();
    if (s == "") return "";
    string[] parts = Regex.Split(s, "(?<=[.!?؟])\\s+");
    if (parts.Length <= 2) return s;
    return (parts[0] + " " + parts[1]).Trim();
}

string StripPersianFrame(string text)
{
    string s = text ?? "";
    s = Regex.Replace(s, "^دُرود بر شُما[\\s\\S]*?اِنتِخاب کَردید\\.?\\s*", "");
    s = Regex.Replace(s, "^درود بر شما[\\s\\S]*?انتخاب کردید\\.?\\s*", "");
    s = Regex.Replace(s, "^درود[^.!?؟]*[.!?؟]?\\s*", "");
    s = Regex.Replace(s, "^سلام[^.!?؟]*[.!?؟]?\\s*", "");
    s = Regex.Replace(s, "\\s*برای اعزام فوری[\\s\\S]*$", "");
    s = Regex.Replace(s, "\\s*چِنانچه مُشکِل[\\s\\S]*$", "");
    s = Regex.Replace(s, "\\s*اگر این راهنمایی[\\s\\S]*$", "");
    s = Regex.Replace(s, "\\s*اَگَر این راهْنَمایی[\\s\\S]*$", "");
    s = Regex.Replace(s, "\\s*برای هماهنگی[\\s\\S]{0,80}تماس بگیرید\\.?", " ");
    s = Regex.Replace(s, "(\\+44\\s*\\(?0?\\)?|0)\\s*7983[\\s-]*759[\\s-]*320", " ");
    s = Regex.Replace(s, "(\\+44\\s*\\(?0?\\)?|0)\\s*203[\\s-]*952[\\s-]*4822", " ");
    s = Regex.Replace(s, "(\\+44\\s*\\(?0?\\)?|0)\\s*800[\\s-]*112[\\s-]*3427", " ");
    s = Regex.Replace(s, "(?<!\\d)(\\+?\\d[\\d\\s-]{6,}\\d)(?!\\d)", " ");
    return TwoFaSentences(Regex.Replace(s, "\\s+", " ").Trim());
}

string CleanTechnicalAnswerForTTS(string text)
{
    string s = StripPersianFrame(text);
    s = Regex.Replace(s, "سردخانه", "سَردخانه");
    s = Regex.Replace(s, "یخچال", "یَخچالِ");
    s = Regex.Replace(s, "کمپرسور", "کُمپرِسور");
    s = Regex.Replace(s, "ترموستات", "تِرموستات");
    s = Regex.Replace(s, "کندانسور", "کُندانسور");
    s = Regex.Replace(s, "اواپراتور", "اِواپُراتور");
    s = Regex.Replace(s, "کولد\\s*دایرکت|ColdDirect|Cold Direct", "کُلد دایرِکت", RegexOptions.IgnoreCase);
    return Regex.Replace(s, "\\s+", " ").Trim();
}

string WrapPersianDisplay(string text)
{
    return FA_DISPLAY_OPEN + "\n" + StripPersianFrame(text) + "\n" + FA_DISPLAY_CLOSE;
}

string PersianAudioText(string text)
{
    if (!string.IsNullOrEmpty(text) && (text.IndexOf("درود بر شما") == 0 || text.IndexOf("دُرود بر شُما") == 0)) return text;
    return FA_AUDIO_OPEN + CleanTechnicalAnswerForTTS(text) + " " + FA_AUDIO_CLOSE;
}

// Accepts any language. Missing phones / Like close are appended, never rejected.
string ParseModelJson(string text, string forceLang)
{
    if (string.IsNullOrEmpty(text)) return null;
    Match m = Regex.Match(text, "\\{[\\s\\S]*\\}");
    if (!m.Success) return null;
    Dictionary<string, object> d;
    try { d = Obj(Json().DeserializeObject(m.Value)); } catch { return null; }
    if (d == null) return null;

    string display = Str(d, "display_text", "spoken_script", "spoken");
    string spokenTts = Str(d, "spoken_text", "tts_text");
    string summary = Str(d, "summary");
    if (display == "" && spokenTts == "" && summary == "") return null;
    if (display == "") display = spokenTts != "" ? spokenTts : summary;
    if (display.Length < 80 && Regex.IsMatch(display, "describe the (make|problem)|tell me (the|your) (make|problem)|let me know (the|your) problem", RegexOptions.IgnoreCase)) return null;

    string code = CanonLang(forceLang);
    if (code == "") code = CanonLang(Str(d, "target_language_code", "language_code", "language"));
    if (code == "") code = DetectLang(display + " " + spokenTts)[0];
    string label = LabelFor(code, Str(d, "language_name", "languageLabel"));

    display = EnsureDisplay(code, display);
    if (spokenTts == "") spokenTts = display;
    spokenTts = EnsureSpoken(code, spokenTts);

    Dictionary<string, object> o = new Dictionary<string, object>();
    o["ok"] = true;
    o["language"] = code == "" ? "en" : code;
    o["languageLabel"] = label;
    o["target_language_code"] = code;
    o["transcript"] = Str(d, "transcript");
    o["spoken"] = display;
    o["display_text"] = display;
    o["tts_text"] = spokenTts;
    o["spoken_text"] = spokenTts;
    o["summary"] = summary == "" ? display : summary;
    o["cause"] = Str(d, "likely_cause", "cause");
    o["checks"] = StrList(d, "quick_checks", "checks");
    o["watermark"] = MARK;
    o["source"] = "llm";
    return Json().Serialize(o);
}

string GeminiDiagnose(string key, string text, string audioB64, string mime, string langHint, string requested)
{
    List<object> parts = new List<object>();
    bool hasAudio = !string.IsNullOrEmpty(audioB64);
    string instr = hasAudio
        ? "The customer's question is in the attached audio recording. Transcribe it exactly in the native script of the language they actually spoke. If they asked to translate or switch language, that requested language WINS and display_text plus spoken_text MUST be entirely in it." + (text != "" ? " They also typed: " + text : "")
        : text;
    if (!string.IsNullOrEmpty(requested))
        instr = "CRITICAL: the user asked for language code '" + requested + "'. Set target_language_code to that language and write display_text and spoken_text ENTIRELY in that language. " + instr;
    else if (!string.IsNullOrEmpty(langHint) && langHint != "auto")
        instr = "The customer selected language '" + langHint + "'. Write display_text and spoken_text 100% in that language. Do not answer in English unless they selected English. " + instr;
    Dictionary<string, object> tp = new Dictionary<string, object>();
    tp["text"] = instr;
    parts.Add(tp);
    if (hasAudio)
    {
        Dictionary<string, object> inline = new Dictionary<string, object>();
        inline["mimeType"] = mime;
        inline["data"] = audioB64;
        Dictionary<string, object> ap = new Dictionary<string, object>();
        ap["inlineData"] = inline;
        parts.Add(ap);
    }
    Dictionary<string, object> sysPart = new Dictionary<string, object>();
    sysPart["text"] = SystemPrompt();
    Dictionary<string, object> sys = new Dictionary<string, object>();
    sys["parts"] = new object[] { sysPart };
    Dictionary<string, object> content = new Dictionary<string, object>();
    content["role"] = "user";
    content["parts"] = parts;

    // gemini-2.x text models return 404 for new keys; 3.8-flash needs ~45s even on low thinking, so it is backup only.
    string[] models = new string[] { "gemini-3.5-flash-lite", "gemini-3.8-flash" };
    foreach (string model in models)
    {
        Dictionary<string, object> gc = new Dictionary<string, object>();
        gc["temperature"] = 0.45;
        gc["responseMimeType"] = "application/json";
        if (model == "gemini-3.8-flash")
        {
            Dictionary<string, object> tc = new Dictionary<string, object>();
            tc["thinkingLevel"] = "low";
            gc["thinkingConfig"] = tc;
        }
        Dictionary<string, object> body = new Dictionary<string, object>();
        body["systemInstruction"] = sys;
        body["contents"] = new object[] { content };
        body["generationConfig"] = gc;
        string url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + Uri.EscapeDataString(key);
        string raw = HttpJson(url, Json().Serialize(body), model == "gemini-3.8-flash" ? 50000 : 25000);
        string parsed = ParseModelJson(ModelText(raw), requested != "" ? requested : langHint);
        if (!string.IsNullOrEmpty(parsed)) return parsed;
    }
    return null;
}

string OpenAiChatRaw(string payload, int timeoutMs)
{
    string key = LoadOpenAi();
    if (key == "") return "";
    Dictionary<string, string> h = new Dictionary<string, string>();
    h["Authorization"] = "Bearer " + key;
    byte[] raw = HttpBytes("POST", "https://api.openai.com/v1/chat/completions", "application/json", Encoding.UTF8.GetBytes(payload), h, timeoutMs);
    if (raw == null) return "";
    return Encoding.UTF8.GetString(raw);
}

string OpenAiMessage(string raw)
{
    try
    {
        Dictionary<string, object> d = Obj(Json().DeserializeObject(raw));
        IList choices = d["choices"] as IList;
        return Str(Obj(Obj(choices[0])["message"]), "content");
    }
    catch { return ""; }
}

string OpenAiDiagnose(string userText, string langHint, string requested)
{
    if (LoadOpenAi() == "") return null;
    string instruction = userText ?? "";
    if (!string.IsNullOrEmpty(requested))
        instruction = "CRITICAL: the user asked for language code '" + requested + "'. Set target_language_code to that language and write display_text and spoken_text ENTIRELY in that language. " + instruction;
    else if (!string.IsNullOrEmpty(langHint) && langHint != "auto")
        instruction = "Preferred language code: " + langHint + ". Write display_text and spoken_text 100% in that language. " + instruction;
    Dictionary<string, object> sys = new Dictionary<string, object>();
    sys["role"] = "system";
    sys["content"] = SystemPrompt();
    Dictionary<string, object> usr = new Dictionary<string, object>();
    usr["role"] = "user";
    usr["content"] = instruction;
    Dictionary<string, object> rf = new Dictionary<string, object>();
    rf["type"] = "json_object";
    string[] models = new string[] { "gpt-4o-mini" };
    foreach (string model in models)
    {
        Dictionary<string, object> body = new Dictionary<string, object>();
        body["model"] = model;
        body["temperature"] = 0.35;
        body["response_format"] = rf;
        body["messages"] = new object[] { sys, usr };
        string raw = OpenAiChatRaw(Json().Serialize(body), 18000);
        string parsed = ParseModelJson(OpenAiMessage(raw), requested != "" ? requested : langHint);
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

const string BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36";

byte[] HttpBytes(string method, string url, string contentType, byte[] body, Dictionary<string, string> headers, int timeoutMs)
{
    try
    {
        ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072;
        HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
        req.Method = method;
        req.Timeout = timeoutMs;
        req.UserAgent = BROWSER_UA;
        if (headers != null)
            foreach (KeyValuePair<string, string> h in headers)
            {
                if (h.Key == "Referer") req.Referer = h.Value;
                else if (h.Key == "Authorization") req.Headers.Add("Authorization", h.Value);
                else req.Headers[h.Key] = h.Value;
            }
        if (body != null)
        {
            req.ContentType = contentType;
            req.ContentLength = body.Length;
            using (Stream s = req.GetRequestStream()) s.Write(body, 0, body.Length);
        }
        using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
        using (Stream rs = resp.GetResponseStream())
        using (MemoryStream ms = new MemoryStream())
        {
            rs.CopyTo(ms);
            return ms.ToArray();
        }
    }
    catch (Exception ex)
    {
        string status = "";
        WebException we = ex as WebException;
        if (we != null && we.Response is HttpWebResponse) status = " HTTP " + (int)((HttpWebResponse)we.Response).StatusCode;
        ttsDiag = ex.GetType().Name + status + ": " + ex.Message;
        return null;
    }
}

string ttsDiag = "";

// Returns {mime, base64} or null. A 429 parks that model until Google's retryDelay (max 6h) so visitors never wait on it.
string[] GeminiTtsModel(string key, string model, string spoken)
{
    string parked = "cd-tts-429-" + model;
    if (HttpRuntime.Cache[parked] != null) return null;
    string line = "Speak in the same language as the text below, as a kind, gentle, professional male engineer. Natural native pronunciation, calm unhurried pace, normal pitch, no slang and no robotic emphasis. Read this exactly:\n\n" + spoken;
    string body = "{\"contents\":[{\"role\":\"user\",\"parts\":[{\"text\":\"" + Esc(line) + "\"}]}],\"generationConfig\":{\"responseModalities\":[\"AUDIO\"],\"speechConfig\":{\"voiceConfig\":{\"prebuiltVoiceConfig\":{\"voiceName\":\"Puck\"}}}}}";
    string url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + Uri.EscapeDataString(key);
    string raw = HttpJson(url, body, 60000) ?? "";
    if (raw.IndexOf("RESOURCE_EXHAUSTED", StringComparison.Ordinal) >= 0 || Regex.IsMatch(raw, "\"code\"\\s*:\\s*429"))
    {
        int secs = 1800;
        Match rd = Regex.Match(raw, "\"retryDelay\"\\s*:\\s*\"(\\d+)");
        if (rd.Success) secs = Math.Max(60, Math.Min(int.Parse(rd.Groups[1].Value), 6 * 3600));
        HttpRuntime.Cache.Insert(parked, "1", null, DateTime.UtcNow.AddSeconds(secs), System.Web.Caching.Cache.NoSlidingExpiration);
        return null;
    }
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
    return new string[] { "audio/wav", Convert.ToBase64String(bin) };
}

string[] GeminiTts(string key, string spoken)
{
    if (string.IsNullOrEmpty(key) || string.IsNullOrEmpty(spoken)) return null;
    foreach (string model in new string[] { "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts" })
    {
        string[] r = GeminiTtsModel(key, model, spoken);
        if (r != null) return r;
    }
    return null;
}

// App_Data/azure-speech.key: line 1 = region (e.g. uksouth), line 2 = key. Official Azure Speech, free tier 500k chars/month.
string[] LoadAzure()
{
    try
    {
        string file = Server.MapPath("~/App_Data/azure-speech.key");
        if (!File.Exists(file)) return null;
        string[] parts = File.ReadAllText(file).Split(new char[] { '\r', '\n', '|' }, StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length < 2 || parts[0].IndexOf("PASTE", StringComparison.OrdinalIgnoreCase) >= 0 || parts[1].IndexOf("PASTE", StringComparison.OrdinalIgnoreCase) >= 0) return null;
        return new string[] { parts[0].Trim().ToLowerInvariant(), parts[1].Trim() };
    }
    catch { return null; }
}

string AzureVoice(string lang)
{
    switch (lang)
    {
        case "fa": return "fa-IR-FaridNeural";
        case "en": return "en-GB-RyanNeural";
        case "tr": return "tr-TR-AhmetNeural";
        case "ar": return "ar-SA-HamedNeural";
        case "es": return "es-ES-AlvaroNeural";
        case "hi": return "hi-IN-MadhurNeural";
        case "ur": return "ur-PK-AsadNeural";
        case "pl": return "pl-PL-MarekNeural";
        case "ro": return "ro-RO-EmilNeural";
        case "de": return "de-DE-ConradNeural";
        case "fr": return "fr-FR-HenriNeural";
        case "it": return "it-IT-DiegoNeural";
        case "pt": return "pt-PT-DuarteNeural";
        case "ru": return "ru-RU-DmitryNeural";
        case "uk": return "uk-UA-OstapNeural";
        case "bn": return "bn-BD-PradeepNeural";
        case "pa": return "pa-IN-OjasNeural";
        case "zh": return "zh-CN-YunxiNeural";
        default: return "en-GB-RyanNeural";
    }
}

string[] AzureTts(string lang, string text)
{
    string[] az = LoadAzure();
    if (az == null || string.IsNullOrEmpty(text)) return null;
    string voice = AzureVoice(lang);
    string xmlLang = voice.Substring(0, 5);
    string ssml = "<speak version='1.0' xml:lang='" + xmlLang + "'><voice name='" + voice + "'><prosody rate='-6%'>" + System.Security.SecurityElement.Escape(text) + "</prosody></voice></speak>";
    Dictionary<string, string> h = new Dictionary<string, string>();
    h["Ocp-Apim-Subscription-Key"] = az[1];
    h["X-Microsoft-OutputFormat"] = "audio-24khz-48kbitrate-mono-mp3";
    byte[] mp3 = HttpBytes("POST", "https://" + az[0] + ".tts.speech.microsoft.com/cognitiveservices/v1", "application/ssml+xml", Encoding.UTF8.GetBytes(ssml), h, 30000);
    if (mp3 == null || mp3.Length < 500) return null;
    return new string[] { "audio/mpeg", Convert.ToBase64String(mp3) };
}

string[] EdgeTts(string text)
{
    if (string.IsNullOrEmpty(text)) return null;
    string dir = Path.GetTempPath();
    string id = Guid.NewGuid().ToString("N");
    string txt = Path.Combine(dir, "cd-fa-" + id + ".txt");
    string pyf = Path.Combine(dir, "cd-fa-" + id + ".py");
    string mp3 = Path.Combine(dir, "cd-fa-" + id + ".mp3");
    try
    {
        File.WriteAllText(txt, text, new UTF8Encoding(false));
        File.WriteAllText(pyf, "import asyncio,edge_tts,sys\nasyncio.run(edge_tts.Communicate(open(sys.argv[1],encoding='utf-8').read(),'fa-IR-FaridNeural').save(sys.argv[2]))\n", new UTF8Encoding(false));
        System.Diagnostics.ProcessStartInfo psi = new System.Diagnostics.ProcessStartInfo("python", "\"" + pyf + "\" \"" + txt + "\" \"" + mp3 + "\"");
        psi.UseShellExecute = false;
        psi.CreateNoWindow = true;
        psi.RedirectStandardError = true;
        psi.RedirectStandardOutput = true;
        using (System.Diagnostics.Process p = System.Diagnostics.Process.Start(psi))
        {
            if (p == null) { ttsDiag = "edge-tts-start"; return null; }
            if (!p.WaitForExit(8000)) { try { p.Kill(); } catch { } ttsDiag = "edge-tts-timeout"; return null; }
            if (p.ExitCode != 0) { ttsDiag = "edge-tts-exit"; return null; }
        }
        if (!File.Exists(mp3)) { ttsDiag = "edge-tts-missing"; return null; }
        byte[] bin = File.ReadAllBytes(mp3);
        if (bin == null || bin.Length < 500) { ttsDiag = "edge-tts-empty"; return null; }
        return new string[] { "audio/mpeg", Convert.ToBase64String(bin) };
    }
    catch (Exception ex) { ttsDiag = "edge-tts " + ex.GetType().Name; return null; }
    finally
    {
        try { File.Delete(txt); } catch { }
        try { File.Delete(pyf); } catch { }
        try { File.Delete(mp3); } catch { }
    }
}

string[] SpeakFa(string text)
{
    string[] r = null;
    try { r = AzureTts("fa", text); } catch { r = null; }
    if (r != null) { ttsDiag = "azure-farid"; return r; }
    try { r = EdgeTts(text); } catch { r = null; }
    if (r != null) { ttsDiag = "edge-farid"; return r; }
    try { r = PiperTts("fa", text); } catch { r = null; }
    if (r != null) { ttsDiag = "piper-ganji"; return r; }
    return null;
}

// Persian voice engines mangle Latin words, digits and undiacritised loanwords (ColdDirect -> "kald
// dayerakat"). Everything sent to a Persian voice goes through here first, so it receives only Persian
// script. The diacritised spellings were checked against the eSpeak phonemes Piper actually produces.
static readonly string[] FA_ONES = { "صفر", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نُه" };
static readonly string[] FA_PHONE_DIGITS = { "صفر", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه" };
static readonly string[] FA_TEENS = { "ده", "یازده", "دوازده", "سیزده", "چهارده", "پانزده", "شانزده", "هفده", "هجده", "نوزده" };
static readonly string[] FA_TENS = { "", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود" };
static readonly string[] FA_HUNDREDS = { "", "صد", "دویست", "سیصد", "چهارصد", "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد" };

static readonly Dictionary<char, string> FA_LETTERS = new Dictionary<char, string> {
    {'A',"اِی"},{'B',"بی"},{'C',"سی"},{'D',"دی"},{'E',"ئی"},{'F',"اِف"},{'G',"جی"},{'H',"اِچ"},{'I',"آی"},
    {'J',"جِی"},{'K',"کِی"},{'L',"اِل"},{'M',"اِم"},{'N',"اِن"},{'O',"اُ"},{'P',"پی"},{'Q',"کیو"},{'R',"آر"},
    {'S',"اِس"},{'T',"تی"},{'U',"یو"},{'V',"وی"},{'W',"دابِلیو"},{'X',"اِکْس"},{'Y',"وای"},{'Z',"زِد"} };

// Latin brand and trade words -> Persian script. Longest first so "cold room" wins over "cold".
static readonly string[,] FA_LATIN = {
    {"colddirect\\.co\\.uk", "کُلد دایرِکت"}, {"cold\\s*direct(\\s*ltd)?", "کُلد دایرِکت"},
    {"foster", "فاسْتِر"}, {"williams", "ویلیامْز"}, {"hoshizaki", "هوشیزاکی"}, {"scotsman", "اِسکاتْس‌مَن"},
    {"polar", "پولار"}, {"gram", "گِرام"}, {"gamko", "گامْکو"}, {"adande", "آدانْد"}, {"precision", "پْرِسیژِن"},
    {"electrolux", "اِلِکْتْرولوکْس"}, {"samsung", "سامْسونْگ"}, {"daikin", "دایْکین"}, {"liebherr", "لیبْهِر"},
    {"tefcold", "تِفْکُلد"}, {"blizzard", "بْلیزارْد"}, {"husky", "هاسْکی"}, {"danfoss", "دانْفاس"},
    {"interlevin", "اینْتِرْلِوین"}, {"dixell", "دیکْسِل"}, {"carel", "کارِل"}, {"eliwell", "اِلیوِل"},
    {"mitsubishi", "میتسوبیشی"}, {"rational", "رَشْنال"}, {"london", "لَندَن"}, {"whatsapp", "واتْس‌اَپ"},
    {"cold\\s*room", "سردخانه"}, {"ice\\s*machine", "یخ‌ساز"}, {"compressor", "کُمپْرِسُر"}, {"condenser", "کندانسور"},
    {"evaporator", "اِواپْراتُر"}, {"thermostat", "ترموستات"}, {"defrost", "برفک‌زدایی"}, {"relay", "رله"},
    {"sensor", "سنسور"}, {"probe", "سنسور"}, {"gasket", "لاستیک در"}, {"controller", "کنترلر"},
    {"fridge", "یخچال"}, {"freezer", "فریزر"}, {"chiller", "چیلر"}, {"fan", "فن"}, {"email", "ایمیل"} };

// Persian spellings that eSpeak reads with wrong vowels unless they carry diacritics.
static readonly string[,] FA_LEXICON = {
    {"کولد\\s*\u200C?\\s*دایرکت", "کُلد دایرِکت"}, {"کلد\\s*\u200C?\\s*دایرکت", "کُلد دایرِکت"}, {"کل\\s*\u200C?\\s*دایرکت", "کُلد دایرِکت"}, {"کمپرسور", "کُمپْرِسُر"}, {"اواپراتور", "اِواپْراتُر"},
    {"فاستر", "فاسْتِر"}, {"ویلیامز", "ویلیامْز"}, {"اسکاتس\u200C?\\s*من", "اِسکاتْس‌مَن"}, {"تکنسین", "تِکْنِسین"} };

string NumFa(long n)
{
    if (n < 0) return "منفی " + NumFa(-n);
    if (n < 10) return FA_ONES[n];
    if (n < 20) return FA_TEENS[n - 10];
    if (n < 100) return FA_TENS[n / 10] + (n % 10 > 0 ? " و " + FA_ONES[n % 10] : "");
    if (n < 1000) return FA_HUNDREDS[n / 100] + (n % 100 > 0 ? " و " + NumFa(n % 100) : "");
    if (n < 1000000) return (n / 1000 == 1 ? "" : NumFa(n / 1000) + " ") + "هزار" + (n % 1000 > 0 ? " و " + NumFa(n % 1000) : "");
    return DigitsFa(n.ToString());
}

string DigitsFa(string digits)
{
    StringBuilder sb = new StringBuilder();
    foreach (char c in digits) if (c >= '0' && c <= '9') sb.Append(sb.Length > 0 ? " " : "").Append(FA_PHONE_DIGITS[c - '0']);
    return sb.ToString();
}

string LettersFa(string letters)
{
    StringBuilder sb = new StringBuilder();
    foreach (char c in letters.ToUpperInvariant()) { string w; if (FA_LETTERS.TryGetValue(c, out w)) sb.Append(sb.Length > 0 ? " " : "").Append(w); }
    return sb.ToString();
}

string NormalizePersianForSpeech(string text)
{
    if (string.IsNullOrEmpty(text)) return "";
    StringBuilder d = new StringBuilder(text.Length);
    foreach (char c in text)
    {
        if (c >= '\u06F0' && c <= '\u06F9') d.Append((char)('0' + (c - '\u06F0')));
        else if (c >= '\u0660' && c <= '\u0669') d.Append((char)('0' + (c - '\u0660')));
        else d.Append(c);
    }
    string s = d.ToString();
    RegexOptions ci = RegexOptions.IgnoreCase;
    const string NOT_LATIN_BEFORE = "(?<![A-Za-z])", NOT_LATIN_AFTER = "(?![A-Za-z])";

    s = Regex.Replace(s, "https?://\\S+|www\\.\\S+", " ", ci);
    s = Regex.Replace(s, "[\\w.+-]+@[\\w-]+(\\.[\\w-]+)+", " ایمیل ما ");
    s = Regex.Replace(s, "(\\+44\\s*\\(?0?\\)?|0)\\s*7983[\\s-]*759[\\s-]*320", " صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر ");
    s = Regex.Replace(s, "(\\+44\\s*\\(?0?\\)?|0)\\s*203[\\s-]*952[\\s-]*4822", " صفر دو صفر سه، نه پنج دو، چهار هشت دو دو ");
    s = Regex.Replace(s, "(\\+44\\s*\\(?0?\\)?|0)\\s*800[\\s-]*112[\\s-]*3427", " صفر هشتصد، یک یک دو، سه چهار دو هفت ");
    s = Regex.Replace(s, "(?<!\\d)(\\+?\\d[\\d\\s-]{6,}\\d)(?!\\d)", delegate (Match m)
    {
        string digits = Regex.Replace(m.Value.Replace("+44", "0"), "\\D", "");
        if (digits.Length < 7) return m.Value;
        List<string> groups = new List<string>();
        for (int i = 0; i < digits.Length; i += 4)
        {
            int n = Math.Min(4, digits.Length - i);
            groups.Add(DigitsFa(digits.Substring(i, n)));
        }
        return " " + string.Join("، ", groups.ToArray()) + " ";
    });
    s = Regex.Replace(s, "([-\u2212]?)(\\d+)\\s*°\\s*[CcFf]?", delegate (Match m)
    {
        return " " + (m.Groups[1].Value.Length > 0 ? "منفی " : "") + NumFa(long.Parse(m.Groups[2].Value)) + " درجه ";
    });
    s = Regex.Replace(s, "(\\d+)\\s*%", delegate (Match m) { return " " + NumFa(long.Parse(m.Groups[1].Value)) + " درصد "; });

    for (int i = 0; i < FA_LATIN.GetLength(0); i++)
        s = Regex.Replace(s, NOT_LATIN_BEFORE + FA_LATIN[i, 0] + NOT_LATIN_AFTER, " " + FA_LATIN[i, 1] + " ", ci);
    s = Regex.Replace(s, NOT_LATIN_BEFORE + "R\\s?-?(\\d{2,4})([A-Za-z]?)" + NOT_LATIN_AFTER, delegate (Match m)
    {
        return " آر " + DigitsFa(m.Groups[1].Value) + (m.Groups[2].Value.Length > 0 ? " " + LettersFa(m.Groups[2].Value) : "") + " ";
    });
    s = Regex.Replace(s, NOT_LATIN_BEFORE + "([A-Za-z]{1,3})\\s?-?(\\d{1,3})(?!\\d)", delegate (Match m)
    {
        return " " + LettersFa(m.Groups[1].Value) + " " + NumFa(long.Parse(m.Groups[2].Value)) + " ";
    });
    s = Regex.Replace(s, NOT_LATIN_BEFORE + "[A-Z]{2,4}" + NOT_LATIN_AFTER, delegate (Match m) { return " " + LettersFa(m.Value) + " "; });
    s = Regex.Replace(s, "\\d+", delegate (Match m)
    {
        if (m.Value.Length >= 4 || m.Value[0] == '0') return " " + DigitsFa(m.Value) + " ";
        return " " + NumFa(long.Parse(m.Value)) + " ";
    });
    s = Regex.Replace(s, "[A-Za-z][A-Za-z'\\-.]*", " ");

    for (int i = 0; i < FA_LEXICON.GetLength(0); i++) s = Regex.Replace(s, FA_LEXICON[i, 0], FA_LEXICON[i, 1]);

    s = s.Replace(':', '،').Replace(';', '؛').Replace(',', '،').Replace('?', '؟');
    s = Regex.Replace(s, "[^\u0600-\u06FF\u200C\\s.!،؛؟]", " ");
    s = Regex.Replace(s, "\\s+", " ");
    s = Regex.Replace(s, "\\s+([.!،؛؟])", "$1");
    s = Regex.Replace(s, "([،؛])(?:\\s*[،؛])+", "$1");
    s = Regex.Replace(s, "[،؛]\\s*([.!؟])", "$1");
    s = Regex.Replace(s, "([.!؟])(?=[^\\s])", "$1 ");
    return s.Trim();
}

// Piper (open-source, runs on this server, no key, no quota). Every voice here is male; there is
// deliberately no female engine anywhere in the chain. Files: App_Data/piper/piper.exe + voices/<model>.onnx(.json).
static readonly System.Threading.SemaphoreSlim piperGate = new System.Threading.SemaphoreSlim(8);

string PiperModel(string lang)
{
    switch (lang)
    {
        case "fa": return "fa_IR-ganji-medium";
        case "en": return "en_GB-alan-medium";
        case "tr": return "tr_TR-dfki-medium";
        case "ar": return "ar_JO-kareem-medium";
        default: return null;
    }
}

// Ganji (Persian narrator) reads a touch faster than the others; output is always at the native sample rate.
string PiperArgs(string lang) { return lang == "fa" ? "--length_scale 1.0 --noise_scale 0.667" : "--length_scale 1.05 --noise_scale 0.667"; }

byte[] PiperRun(string exe, string dir, string onnx, string line, string args)
{
    if (!piperGate.Wait(30000)) { ttsDiag = "piper-busy"; return null; }
    try
    {
       System.Diagnostics.ProcessStartInfo psi = new System.Diagnostics.ProcessStartInfo(exe,
            "-m \"" + onnx + "\" --output_raw " + args + " --sentence_silence 0.25");
        psi.WorkingDirectory = dir;
        psi.UseShellExecute = false;
        psi.CreateNoWindow = true;
        psi.RedirectStandardInput = true;
        psi.RedirectStandardOutput = true;
        psi.RedirectStandardError = true;
        using (System.Diagnostics.Process p = System.Diagnostics.Process.Start(psi))
        {
            p.ErrorDataReceived += delegate { };
            p.BeginErrorReadLine();
            MemoryStream pcm = new MemoryStream();
            Stream stdout = p.StandardOutput.BaseStream;
            System.Threading.Tasks.Task reader = System.Threading.Tasks.Task.Factory.StartNew(delegate { stdout.CopyTo(pcm); });
            byte[] input = new UTF8Encoding(false).GetBytes(line + "\n");
            p.StandardInput.BaseStream.Write(input, 0, input.Length);
            p.StandardInput.BaseStream.Flush();
            p.StandardInput.Close();
            if (!reader.Wait(60000))
            {
                try { p.Kill(); } catch { }
                ttsDiag = "piper-timeout";
                return null;
            }
            p.WaitForExit(5000);
            byte[] raw = pcm.ToArray();
            if (raw.Length < 2000) { ttsDiag = "piper-empty exit=" + (p.HasExited ? p.ExitCode.ToString() : "?"); return null; }
            if ((raw.Length & 1) == 1) Array.Resize(ref raw, raw.Length - 1);
            return raw;
        }
    }
    catch (Exception ex) { ttsDiag = "piper " + ex.GetType().Name; return null; }
    finally { piperGate.Release(); }
}

List<string> SentenceGroups(string text, int max)
{
    List<string> groups = new List<string>();
    StringBuilder cur = new StringBuilder();
    foreach (string s in Regex.Split(text, "(?<=[.!?\u061F\u06D4\u2026])\\s+"))
    {
        if (s.Length == 0) continue;
        if (cur.Length > 0 && cur.Length + 1 + s.Length > max) { groups.Add(cur.ToString()); cur.Length = 0; }
        if (cur.Length > 0) cur.Append(' ');
        cur.Append(s);
    }
    if (cur.Length > 0) groups.Add(cur.ToString());
    return groups;
}

// Each sentence group runs in its own Piper process in parallel, then the PCM is joined in order.
string[] PiperTts(string lang, string text)
{
    string model = PiperModel(lang);
    if (model == null || string.IsNullOrEmpty(text)) return null;
    string dir = Server.MapPath("~/App_Data/piper");
    string exe = Path.Combine(dir, "piper.exe");
    string onnx = Path.Combine(dir, "voices", model + ".onnx");
    if (!File.Exists(exe) || !File.Exists(onnx) || !File.Exists(onnx + ".json")) { ttsDiag = "piper-missing:" + model; return null; }
    int rate = 22050;
    try
    {
        Match sr = Regex.Match(File.ReadAllText(onnx + ".json"), "\"sample_rate\"\\s*:\\s*(\\d+)");
        if (sr.Success) rate = int.Parse(sr.Groups[1].Value);
    }
    catch { }
    List<string> groups = SentenceGroups(Regex.Replace(text, "\\s+", " ").Trim(), 120);
    if (groups.Count == 0 || groups.Count > 24) return null;
    string args = PiperArgs(lang);
    byte[][] parts = new byte[groups.Count][];
    System.Threading.Tasks.Parallel.For(0, groups.Count, new System.Threading.Tasks.ParallelOptions { MaxDegreeOfParallelism = 6 },
        delegate (int i) { parts[i] = PiperRun(exe, dir, onnx, groups[i], args); });
        byte[] gap = new byte[Math.Max(2, (rate / 50) * 2)];
    using (MemoryStream all = new MemoryStream())
    {
        for (int i = 0; i < parts.Length; i++)
        {
            if (parts[i] == null) return null;
            if (i > 0) all.Write(gap, 0, gap.Length);
            all.Write(parts[i], 0, parts[i].Length);
        }
        return new string[] { "audio/wav", Convert.ToBase64String(PcmToWav(all.ToArray(), rate)) };
    }
}

// A short first part means the voice starts sooner; split a long opening sentence at its first comma.
List<string> StreamGroups(string text)
{
    List<string> groups = SentenceGroups(Regex.Replace(text, "\\s+", " ").Trim(), 120);
    int[] limits = { 70, 90 };
    for (int i = 0; i < limits.Length && i < groups.Count; i++)
    {
        if (groups[i].Length <= limits[i]) continue;
        Match m = Regex.Match(groups[i], "^(.{12," + limits[i] + "}[,\u060C;:!])\\s+(.+)$");
        if (m.Success) { groups[i] = m.Groups[1].Value; groups.Insert(i + 1, m.Groups[2].Value); }
    }
    return groups;
}

string LoadOpenAi()
{
    try
    {
        string file = Server.MapPath("~/App_Data/openai-voice.key");
        if (!File.Exists(file)) return "";
        string k = File.ReadAllText(file).Trim();
        if (k == "" || k.IndexOf("PASTE", StringComparison.OrdinalIgnoreCase) >= 0) return "";
        return k.Split(new char[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)[0].Trim();
    }
    catch { return ""; }
}

string[] OpenAiTts(string text)
{
    string key = LoadOpenAi();
    if (key == "" || string.IsNullOrEmpty(text)) return null;
    if (text.Length > 4000) text = text.Substring(0, 4000);
    string body = "{\"model\":\"gpt-4o-mini-tts\",\"voice\":\"onyx\",\"input\":\"" + Esc(text) + "\",\"response_format\":\"mp3\"}";
    Dictionary<string, string> h = new Dictionary<string, string>();
    h["Authorization"] = "Bearer " + key;
    byte[] mp3 = HttpBytes("POST", "https://api.openai.com/v1/audio/speech", "application/json", Encoding.UTF8.GetBytes(body), h, 45000);
    if (mp3 == null || mp3.Length < 2000) return null;
    return new string[] { "audio/mpeg", Convert.ToBase64String(mp3) };
}

// Google speech stream for languages with no local Piper voice. Never used for Persian (HTTP 400).
string TranslateTl(string lang)
{
    if (lang == "fa" || lang == "") return null;
    if (lang == "en") return "en-GB";
    if (lang == "zh") return "zh-CN";
    if (lang == "tl" || lang == "fil") return "tl";
    if (lang == "jw") return "jw";
    return lang;
}

string[] TranslateTts(string lang, string text)
{
    string tl = TranslateTl(lang);
    if (tl == null || string.IsNullOrEmpty(text)) return null;
    List<string> chunks = SentenceGroups(Regex.Replace(text, "\\s+", " ").Trim(), 180);
    if (chunks.Count == 0 || chunks.Count > 30) return null;
    Dictionary<string, string> h = new Dictionary<string, string>();
    h["Referer"] = "https://translate.google.com/";
    using (MemoryStream all = new MemoryStream())
    {
        for (int i = 0; i < chunks.Count; i++)
        {
            string url = "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=" + Uri.EscapeDataString(tl)
                + "&total=" + chunks.Count + "&idx=" + i + "&textlen=" + chunks[i].Length + "&q=" + Uri.EscapeDataString(chunks[i]);
            byte[] part = HttpBytes("GET", url, null, null, h, 15000) ?? HttpBytes("GET", url, null, null, h, 15000);
            if (part == null || part.Length < 200) return null;
            all.Write(part, 0, part.Length);
        }
        return new string[] { "audio/mpeg", Convert.ToBase64String(all.ToArray()) };
    }
}

// OpenAI onyx (if a key is installed) -> Puck -> Piper (fa/en/tr/ar) -> Azure -> Google stream for every other language.
string[] Speak(string key, string lang, string text, out string voice)
{
    voice = "none";
    if (string.IsNullOrEmpty(text)) return null;
    lang = CanonLang(lang);
    if (lang == "fa")
    {
        text = PersianAudioText(text);
        string[] fa = SpeakFa(text);
        if (fa != null) { voice = ttsDiag; return fa; }
        voice = "none";
        return null;
    }
    string[] r = null;
    try { r = OpenAiTts(text); } catch { r = null; }
    if (r != null) { voice = "openai-onyx"; return r; }
    try { r = GeminiTts(key, text); } catch { r = null; }
    if (r != null) { voice = "Puck"; return r; }
    r = PiperTts(lang, text);
    if (r != null) { voice = "piper-" + PiperModel(lang); return r; }
    try { r = AzureTts(lang, text); } catch { r = null; }
    if (r != null) { voice = "azure-neural"; return r; }
    try { r = TranslateTts(lang, text); } catch { r = null; }
    if (r != null) { voice = "cloud-neural-fallback"; return r; }
    return null;
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
    Dictionary<string, object> req = null;
    try { req = Obj(Json().DeserializeObject(rawJson)); } catch { req = null; }
    string mode = (Str(req, "mode") != "" ? Str(req, "mode") : (Request.QueryString["mode"] ?? "")).Trim().ToLowerInvariant();
    string text = Str(req, "text");
    if (text.Length > 2000) text = text.Substring(0, 2000);
    string audioIn = Regex.Replace(Str(req, "audio"), "\\s+", "");
    if (audioIn.Length > 8000000) audioIn = "";
    string mime = Str(req, "mime").ToLowerInvariant();
    int semi = mime.IndexOf(';');
    if (semi >= 0) mime = mime.Substring(0, semi).Trim();
    if (!Regex.IsMatch(mime, "^audio/[a-z0-9.+-]{2,30}$")) mime = "audio/webm";
    string key = LoadKey();
    Response.ContentType = "application/json";

    if (mode == "tts")
    {
        string say = text.Length > 2500 ? text.Substring(0, 2500) : text;
        string lang = CanonLang(Str(req, "language", "lang"));
        if (lang == "") lang = CanonLang(Request.QueryString["lang"] ?? "");
        if (lang == "") lang = DetectLang(say)[0];
        bool piperOnly = Str(req, "engine").ToLowerInvariant() == "piper";
        string v = "none";
        string[] spoken = null;
        List<string> more = new List<string>();
        if (lang == "fa")
        {
            say = PersianAudioText(say);
            spoken = SpeakFa(say);
            if (spoken != null) v = string.IsNullOrEmpty(ttsDiag) ? "fa-IR-FaridNeural" : ttsDiag;
        }
        else if (!piperOnly)
        {
            try { spoken = OpenAiTts(say); } catch { spoken = null; }
            if (spoken != null) v = "openai-onyx";
            if (spoken == null)
            {
                try { spoken = GeminiTts(key, say); } catch { spoken = null; }
                if (spoken != null) v = "Puck";
            }
        }
        if (spoken == null && PiperModel(lang) != null)
        {
            List<string> groups = piperOnly ? new List<string> { Regex.Replace(say, "\\s+", " ").Trim() } : StreamGroups(say);
            if (groups.Count > 0 && groups.Count <= 25)
            {
                spoken = PiperTts(lang, groups[0]);
                if (spoken != null) { v = "piper-" + PiperModel(lang); more = groups.GetRange(1, groups.Count - 1); }
            }
        }
        if (spoken == null && !piperOnly)
        {
            try { spoken = AzureTts(lang, say); } catch { spoken = null; }
            if (spoken != null) v = "azure-neural";
            if (spoken == null)
            {
                try { spoken = TranslateTts(lang, say); } catch { spoken = null; }
                if (spoken != null) v = "cloud-neural-fallback";
            }
        }
        Dictionary<string, object> o = new Dictionary<string, object>();
        o["ok"] = spoken != null;
        o["voice"] = spoken != null ? v : "none";
        o["language"] = lang;
        o["tts_text"] = say;
        if (spoken != null) { o["audio_mime"] = spoken[0]; o["audio_base64"] = spoken[1]; o["more"] = more; }
        else { o["error"] = "No voice available for this language right now."; o["detail"] = ttsDiag; }
        o["watermark"] = MARK;
        Response.Write(Json().Serialize(o));
        return;
    }

    if (text == "" && audioIn == "")
    {
        Response.StatusCode = 400;
        Response.Write("{\"ok\":false,\"error\":\"Type a fault or speak, then try again.\",\"watermark\":\"" + MARK + "\"}");
        return;
    }

    string requested = RequestedLang(text);
    string hint = requested != "" ? requested : CanonLang(Str(req, "langHint", "language"));
    string result = null;
    if (audioIn == "" && LoadOpenAi() != "")
    {
        try { result = OpenAiDiagnose(text, hint, requested); } catch { result = null; }
    }
    if (string.IsNullOrEmpty(result) && key != "")
    {
        try { result = GeminiDiagnose(key, text, audioIn, mime, hint, requested); } catch { result = null; }
    }
    if (string.IsNullOrEmpty(result) && audioIn != "" && LoadOpenAi() != "" && text != "")
    {
        try { result = OpenAiDiagnose(text, hint, requested); } catch { result = null; }
    }
    if (string.IsNullOrEmpty(result))
    {
        if (text == "" && audioIn != "")
        {
            Response.StatusCode = 502;
            Response.Write("{\"ok\":false,\"error\":\"Sorry, I couldn't make out that recording. Tap SPEAK and try again, or type the fault.\",\"watermark\":\"" + MARK + "\"}");
            return;
        }
        result = FallbackJson(text != "" ? text : "fridge not cooling", hint);
    }

    string voice = "pending";
    try
    {
        string lang = JsonField(result, "language");
        string say = JsonField(result, "tts_text");
        if (say == "") say = JsonField(result, "spoken_text");
        if (say == "") say = JsonField(result, "spoken");
        string vOut = "none";
        string[] clip = Speak(key, lang, say, out vOut);
        if (clip != null)
        {
            voice = string.IsNullOrEmpty(vOut) ? "embedded" : vOut;
            result = AddField(result, "audio_mime", "\"" + clip[0] + "\"");
            result = AddField(result, "audio_base64", "\"" + clip[1] + "\"");
            result = AddField(result, "audio", "{\"mime\":\"" + clip[0] + "\",\"data\":\"" + clip[1] + "\"}");
        }
        else voice = "browser-tts-failed";
    }
    catch { voice = "browser-tts-failed"; }
    result = AddField(result, "voice", "\"" + voice + "\"");
    Response.Write(result);
}
</script>
