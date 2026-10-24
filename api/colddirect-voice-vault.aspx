<%@ Page Language="C#" EnableSessionState="false" ValidateRequest="false" %>
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
    return Regex.Unescape(m.Groups[1].Value);
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
    return "You are the Head Engineer at ColdDirect Ltd (colddirect.co.uk), 27 Felixstowe Road, Enfield, London N9 0DX. You have 30 years of hands-on commercial refrigeration and catering-equipment experience across London. CRITICAL LANGUAGE LOCK - ZERO MIXING: Detect the exact language. If English, reply 100% in warm conversational British English and never mix Farsi. If Persian, reply 100% in warm everyday colloquial Tehran spoken Persian with no bookish words such as می\u200cباشد. If any other language, reply only in that language. Every spoken answer must introduce you as Head Engineer at ColdDirect with 30 years of experience, explain the fault warmly, spell numbers and error codes phonetically, and end by asking for a Like or 5-star review. Commercial refrigeration and catering only. Return STRICT JSON: {\"language\":\"en\",\"languageLabel\":\"English\",\"spoken\":\"...\",\"summary\":\"...\",\"cause\":\"...\",\"checks\":[\"...\"]}";
}

string[] DetectLang(string text)
{
    if (Regex.IsMatch(text ?? "", "[پچژگ]|[آ-ی]")) return new string[] { "fa", "Persian" };
    if (Regex.IsMatch(text ?? "", "[\\u0600-\\u06FF]")) return new string[] { "ar", "Arabic" };
    if (Regex.IsMatch(text ?? "", "[ğüşöçıİĞÜŞÖÇ]")) return new string[] { "tr", "Turkish" };
    if (Regex.IsMatch(text ?? "", "[\\u0900-\\u097F]")) return new string[] { "hi", "Hindi" };
    return new string[] { "en", "English" };
}

string FallbackJson(string text)
{
    string[] lang = DetectLang(text);
    string q = (text ?? "").ToLowerInvariant();
    string kind = "generic";
    if (Regex.IsMatch(q, "e\\s*1|e1") || (q.IndexOf("foster") >= 0 && q.IndexOf("fridge") >= 0)) kind = "e1";
    else if (Regex.IsMatch(q, "ice machine|not making ice|یخساز")) kind = "ice";
    else if (Regex.IsMatch(q, "cold room|ice-?up|سردخانه")) kind = "room";

    string spoken, summary, cause, checks;
    if (lang[0] == "fa")
    {
        if (kind == "e1")
        {
            spoken = "سلام رفیق، من سرمهندس کلد دایرکت‌ام، سی ساله تو لندن روی یخچال و سردخونه و کترینگ کار کردم. گفتی فاستر کد ای‌وان نشون می‌ده - ای مثل حرف ای، وان یعنی عدد یک. معمولاً یعنی کابین گرم شده یا سنسور دما شل شده یا یخ زده. اول کندانسور بالای دستگاه رو ببین گردوخاک نبسته باشه، لاستیک در رو چک کن و ببین باد برگشتی بسته نشده. اگه دمای داخل از هشت درجه بالاتر رفته همون روز می‌آیم. لطفاً دکمه لایک یا پنج ستاره رو بزن تا کلد دایرکت بتونه رشد کنه. زنگ بزن صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر.";
            summary = "کد ای‌وان فاستر معمولاً آلارم دمای بالا یا خرابی سنسور کابینه.";
            cause = "کندانسور کثیف، در باز مونده یا لاستیک ضعیف، جریان هوا بسته، یا سنسور خراب.";
            checks = "[\"کندانسور بالا رو تمیز کن.\",\"ببین در کامل بسته می‌شه و فن‌ها می‌چرخن.\",\"اگه دما بالای ۸ درجه است با 07983 759320 تماس بگیر.\"]";
        }
        else if (kind == "ice")
        {
            spoken = "سلام، من سرمهندس کلد دایرکت‌ام، سی ساله تو لندن یخساز و کترینگ درست کردم. اگه یخساز یخ نمی‌ده اول آب و رسوب و گرما رو چک می‌کنیم. شیر آب باز باشه، فیلتر نگرفته باشه و کندانسور تمیز باشه. لایک یا پنج ستاره بزن تا کمک کنی رشد کنیم. زنگ بزن صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر.";
            summary = "نبودن یخ معمولاً از آب، رسوب اواپراتور یا کندانسور کثیفه.";
            cause = "شیر بسته، فیلتر گرفته، رسوب یا کندانسور کثیف.";
            checks = "[\"ببین آب به دستگاه می‌رسه.\",\"اگه ورقه یخ نازک و ناهماهنگه، رسوبه.\",\"کندانسور رو تمیز کن و اگر درست نشد 07983 759320.\"]";
        }
        else if (kind == "room")
        {
            spoken = "سلام، من سرمهندس کلد دایرکت‌ام، سی ساله سردخونه‌های لندن رو درست کردم. یخ زدن اواپراتور یعنی اتاق نفس نمی‌کشه. یا هوای گرم داره می‌آد تو، یا برفک‌زدایی خوابیده. یخ رو نشکون. لایک یا پنج ستاره بزن لطفاً. زنگ بزن صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر.";
            summary = "یخ زدن سردخانه معمولاً از نفوذ هوا از در یا خوابیدن سیکل دیفراسته.";
            cause = "در باز، لاستیک ضعیف، هیتر دیفراست خراب یا درین گرفته.";
            checks = "[\"در، پرده و لاستیک رو چک کن.\",\"ببین لوله درین بازه.\",\"موجودی رو حفظ کن و به 07983 759320 زنگ بزن.\"]";
        }
        else
        {
            spoken = "سلام رفیق، من سرمهندس کلد دایرکت‌ام، سی ساله تو لندن روی سرمایش تجاری و کترینگ کار کردم. برند، کد خطا و اینکه کابین هنوز سرده یا نه رو بگو تا راهنمایی‌ت کنم. لطفاً لایک یا پنج ستاره بزن تا کلد دایرکت رشد کنه. زنگ بزن صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر.";
            summary = "برند، کد خطا و دمای فعلی رو بگو.";
            cause = "بدون برند و کد خطا دقیق نمی‌شه گفت؛ معمولاً کندانسور، کنترلر یا لاستیک در.";
            checks = "[\"برند و کد روی کنترلر رو یادداشت کن.\",\"کندانسور و لاستیک در رو چک کن.\",\"اگه موجودی گرم می‌شه 07983 759320.\"]";
        }
    }
    else
    {
        if (kind == "e1")
        {
            spoken = "Hello, I am the Head Engineer at ColdDirect. I have thirty years of hands-on commercial refrigeration and catering experience here in London. You mentioned a Foster fridge showing E one - that is E for Echo, one as in the number one. On Foster controllers that is usually a high-temperature or probe alarm. Brush the top condenser, check the door gasket is sucking shut, and keep stock off the return air. If food is above eight degrees Celsius we should attend the same day. Please tap Helpful or leave a five-star review so ColdDirect can keep growing. Call oh seven nine eight three, seven five nine, three two oh.";
            summary = "Foster E1 is typically a high-temperature or cabinet-probe alarm.";
            cause = "Dirty condenser, door left open or a weak gasket, blocked airflow, or a failed probe.";
            checks = "[\"Brush the top condenser until you can see the fins.\",\"Confirm the door closes on a clean gasket and the fans are spinning.\",\"If cabinet air is above 8°C, call 07983 759320.\"]";
        }
        else if (kind == "ice")
        {
            spoken = "Hello, I am the Head Engineer at ColdDirect, thirty years on ice machines and catering kit across London. If the ice machine is not making ice, start with water, scale and heat rejection. Check the tap is open, the inlet filter is clear, the bin switch is free, and the condenser is clean. Please tap Like or leave a five-star review to help ColdDirect grow. Call oh seven nine eight three, seven five nine, three two oh.";
            summary = "No ice usually means water supply, scale, a dirty condenser, or a harvest/bin switch fault.";
            cause = "Closed stopcock, blocked inlet filter, limescale, dirty condenser, or a bin switch that thinks the bin is full.";
            checks = "[\"Confirm water is reaching the machine and the filter is not blocked.\",\"Look for a thin, uneven ice sheet that will not drop - that is scale.\",\"Clean the condenser and call 07983 759320 if it still will not harvest.\"]";
        }
        else if (kind == "room")
        {
            spoken = "Hello, I am the Head Engineer at ColdDirect with thirty years on London walk-in cold rooms. Ice-up on the evaporator means the room cannot breathe. Warm moist air is getting in, or defrost has stopped. Do not chip the coil. Please tap Helpful or leave a five-star review so ColdDirect can keep improving. For same-day help call oh seven nine eight three, seven five nine, three two oh.";
            summary = "Cold-room ice-up is usually door air ingress or a failed defrost cycle.";
            cause = "Door left open or a tired gasket, failed defrost heater or probe, or a blocked drain.";
            checks = "[\"Check the door closer, strip curtains and gasket.\",\"See if the drain line is clear and the coil is a solid ice block.\",\"Protect stock and call 07983 759320 - do not smash ice off the fins.\"]";
        }
        else
        {
            spoken = "Hello, I am the Head Engineer at ColdDirect. I have thirty years of hands-on commercial refrigeration and catering experience in London. Tell me the make, the error code and whether the cabinet is still cold, and I will talk you through the safe checks. Please tap the Like button or leave a five-star review to help ColdDirect grow. Call oh seven nine eight three, seven five nine, three two oh whenever you want an engineer.";
            summary = "Describe the make, error code and whether the cabinet is still holding temperature.";
            cause = "Needs the symptom, brand and error code to narrow - condenser, controls or door integrity are the usual London call-outs.";
            checks = "[\"Note the brand, model and any code on the controller.\",\"Feel the condenser and confirm the door gasket seals.\",\"Call 07983 759320 if stock is warming.\"]";
        }
    }

    return "{\"ok\":true,\"language\":\"" + Esc(lang[0]) + "\",\"languageLabel\":\"" + Esc(lang[1]) + "\",\"spoken\":\"" + Esc(spoken) + "\",\"summary\":\"" + Esc(summary) + "\",\"cause\":\"" + Esc(cause) + "\",\"checks\":" + checks + ",\"watermark\":\"" + MARK + "\",\"source\":\"vault-fallback\"}";
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
    return Regex.Unescape(m.Groups[1].Value);
}

string ParseModelJson(string text)
{
    if (string.IsNullOrEmpty(text)) return null;
    Match m = Regex.Match(text, "\\{[\\s\\S]*\\}");
    if (!m.Success) return null;
    string block = m.Value;
    if (block.IndexOf("\"spoken\"") < 0 && block.IndexOf("\"summary\"") < 0) return null;
    if (block.IndexOf("\"watermark\"") < 0)
        block = block.TrimEnd().TrimEnd('}') + ",\"watermark\":\"" + MARK + "\",\"source\":\"gemini\"}";
    return block;
}

string GeminiDiagnose(string key, string text)
{
    string prompt = Esc(SystemPrompt());
    string user = Esc(string.IsNullOrEmpty(text) ? "Please diagnose this commercial refrigeration fault." : text);
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
    Response.Cache.SetCacheability(HttpCacheability.NoCache);
    Response.AddHeader("X-Content-Type-Options", "nosniff");
    Response.AddHeader("X-CD-IP", MARK);

    string origin = RequestOrigin();
    if (origin == "")
    {
        Response.StatusCode = 403;
        Response.ContentType = "text/plain; charset=utf-8";
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
        Response.ContentType = "application/json; charset=utf-8";
        Response.Write("{\"ok\":false,\"error\":\"POST only\",\"watermark\":\"" + MARK + "\"}");
        Response.End();
        return;
    }

    string rawJson = "";
    using (StreamReader sr = new StreamReader(Request.InputStream, Encoding.UTF8))
        rawJson = sr.ReadToEnd();
    string text = (JsonField(rawJson, "text") ?? "").Trim();
    if (text.Length > 2000) text = text.Substring(0, 2000);
    if (text == "")
    {
        Response.StatusCode = 400;
        Response.ContentType = "application/json; charset=utf-8";
        Response.Write("{\"ok\":false,\"error\":\"Type a fault or speak, then try again.\",\"watermark\":\"" + MARK + "\"}");
        Response.End();
        return;
    }

    string key = LoadKey();
    string result = null;
    if (key != "")
    {
        try { result = GeminiDiagnose(key, text); } catch { result = null; }
    }
    if (string.IsNullOrEmpty(result)) result = FallbackJson(text);

    Response.ContentType = "application/json; charset=utf-8";
    Response.Write(result);
}
</script>
