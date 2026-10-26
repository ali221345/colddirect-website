<%@ Page Language="C#" EnableSessionState="false" ValidateRequest="false" ResponseEncoding="utf-8" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Net" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.Text.RegularExpressions" %>
<%@ Import Namespace="System.Web.Script.Serialization" %>
<script runat="server">
const string SYS = "You are a speech-to-text transcriber. Task=transcribe only. NEVER translate. NEVER convert speech into English. If they spoke Persian/Farsi, transcript MUST be Persian script, not an English translation. Arabic stays Arabic. Turkish stays Turkish. Chinese stays Chinese. JSON only: {\"language\":\"ISO-639-1\",\"transcript\":\"verbatim original text\"}. language is the spoken language, not English, unless they actually spoke English.";

bool HostOk(string value)
{
    if (string.IsNullOrEmpty(value)) return false;
    try
    {
        Uri u = new Uri(value);
        string host = (u.Host ?? "").ToLowerInvariant();
        if (host == "localhost" || host == "127.0.0.1") return true;
        return host == "colddirect.co.uk" || host == "www.colddirect.co.uk";
    }
    catch { return false; }
}

string RequestOrigin()
{
    string origin = Request.Headers["Origin"] ?? "";
    if (HostOk(origin)) return origin;
    try
    {
        string referer = Request.Headers["Referer"] ?? "";
        if (HostOk(referer))
        {
            Uri u = new Uri(referer);
            return u.Scheme + "://" + u.Host;
        }
    }
    catch { }
    return "";
}

string LoadGemini()
{
    try
    {
        string env = Environment.GetEnvironmentVariable("GEMINI_API_KEY") ?? Environment.GetEnvironmentVariable("GOOGLE_API_KEY") ?? "";
        if (!string.IsNullOrEmpty(env)) return env.Trim();
        string file = Server.MapPath("~/App_Data/gemini-voice.key");
        if (File.Exists(file))
        {
            string k = File.ReadAllText(file).Trim();
            if (k.IndexOf("PASTE", StringComparison.OrdinalIgnoreCase) >= 0) return "";
            return k;
        }
    }
    catch { }
    return "";
}

string JsonField(string json, string key)
{
    Match m = Regex.Match(json ?? "", "\"" + Regex.Escape(key) + "\"\\s*:\\s*\"((?:\\\\.|[^\"])*)\"");
    if (!m.Success) return "";
    try { return Regex.Unescape(m.Groups[1].Value); } catch { return m.Groups[1].Value; }
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

string ModelText(string raw)
{
    if (string.IsNullOrEmpty(raw)) return "";
    Match m = Regex.Match(raw, "\"text\"\\s*:\\s*\"((?:\\\\.|[^\"])*)\"");
    if (!m.Success) return "";
    try { return Regex.Unescape(m.Groups[1].Value); } catch { return m.Groups[1].Value; }
}

void Fail(int status, string code)
{
    Response.StatusCode = status;
    Response.TrySkipIisCustomErrors = true;
    Response.Write("{\"ok\":false,\"error\":\"" + code + "\"}");
}
</script>
<%
Response.ContentType = "application/json; charset=utf-8";
Response.Charset = "utf-8";
Response.TrySkipIisCustomErrors = true;
Response.Cache.SetCacheability(HttpCacheability.NoCache);
string origin = RequestOrigin();
if (!string.IsNullOrEmpty(origin))
{
    Response.AddHeader("Access-Control-Allow-Origin", origin);
    Response.AddHeader("Vary", "Origin");
}
if (Request.HttpMethod == "OPTIONS")
{
    Response.AddHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    Response.AddHeader("Access-Control-Allow-Headers", "Content-Type");
    Response.End();
}
if (Request.HttpMethod != "POST")
{
    Fail(405, "method");
    Response.End();
}
string key = LoadGemini();
if (string.IsNullOrEmpty(key))
{
    Fail(200, "missing_key");
    Response.End();
}
string body;
using (StreamReader sr = new StreamReader(Request.InputStream, Encoding.UTF8))
    body = sr.ReadToEnd();
string audio = JsonField(body, "audio_base64");
if (string.IsNullOrEmpty(audio)) audio = JsonField(body, "audio");
string mime = JsonField(body, "mime");
if (string.IsNullOrEmpty(mime) || !Regex.IsMatch(mime, "^audio/[a-z0-9.+-]{2,30}$")) mime = "audio/wav";
if (string.IsNullOrEmpty(audio) || audio.Length < 80)
{
    Fail(200, "no_audio");
    Response.End();
}
string payload = "{"
    + "\"systemInstruction\":{\"parts\":[{\"text\":" + new JavaScriptSerializer().Serialize(SYS) + "}]},"
    + "\"contents\":[{\"role\":\"user\",\"parts\":["
    + "{\"text\":\"Transcribe verbatim in the original spoken language. Do not translate into English.\"},"
    + "{\"inlineData\":{\"mimeType\":" + new JavaScriptSerializer().Serialize(mime) + ",\"data\":" + new JavaScriptSerializer().Serialize(audio) + "}}"
    + "]}],"
    + "\"generationConfig\":{\"temperature\":0,\"maxOutputTokens\":120,\"responseMimeType\":\"application/json\"}"
    + "}";
string raw = HttpJson("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key=" + Uri.EscapeDataString(key), payload, 9000);
string text = ModelText(raw);
string lang = JsonField(text, "language").ToLowerInvariant();
string transcript = JsonField(text, "transcript");
if (string.IsNullOrEmpty(transcript)) transcript = JsonField(text, "text");
if (string.IsNullOrEmpty(transcript))
{
    Fail(200, "no_transcript");
    Response.End();
}
if (lang.IndexOf("-") > 0) lang = lang.Split('-')[0];
JavaScriptSerializer ser = new JavaScriptSerializer();
Response.Write("{\"ok\":true,\"mode\":\"transcribe\",\"language\":" + ser.Serialize(lang) + ",\"transcript\":" + ser.Serialize(transcript) + "}");
%>
