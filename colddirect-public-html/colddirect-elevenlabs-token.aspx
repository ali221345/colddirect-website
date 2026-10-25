<%@ Page Language="C#" EnableSessionState="false" ValidateRequest="false" ResponseEncoding="utf-8" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Net" %>
<%@ Import Namespace="System.Text" %>
<script runat="server">
const string AGENT_ID = "agent_2901m5th5arfe9kamcec9ef2p42q";
const string TOKEN_URL = "https://api.elevenlabs.io/v1/convai/conversation/token?agent_id=" + AGENT_ID + "&source=js_sdk";

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

string LoadKey()
{
    try
    {
        string env = Environment.GetEnvironmentVariable("ELEVENLABS_API_KEY") ?? Environment.GetEnvironmentVariable("XI_API_KEY") ?? "";
        if (!string.IsNullOrEmpty(env)) return env.Trim();
        string file = Server.MapPath("~/App_Data/elevenlabs.key");
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

string HttpGet(string url, string apiKey)
{
    try
    {
        ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072;
        HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
        req.Method = "GET";
        req.Timeout = 12000;
        req.Headers["xi-api-key"] = apiKey;
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

string ExtractToken(string json)
{
    if (string.IsNullOrEmpty(json)) return "";
    string[] keys = new string[] { "\"token\"", "\"conversation_token\"", "\"signed_url\"" };
    foreach (string key in keys)
    {
        int i = json.IndexOf(key, StringComparison.OrdinalIgnoreCase);
        if (i < 0) continue;
        int colon = json.IndexOf(':', i);
        if (colon < 0) continue;
        int q1 = json.IndexOf('"', colon + 1);
        if (q1 < 0) continue;
        int q2 = json.IndexOf('"', q1 + 1);
        if (q2 <= q1) continue;
        return json.Substring(q1 + 1, q2 - q1 - 1);
    }
    return "";
}

void Fail(int status, string code)
{
    Response.StatusCode = status;
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
    Response.AddHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
    Response.AddHeader("Access-Control-Allow-Headers", "Content-Type");
    Response.End();
}
if (Request.HttpMethod != "GET")
{
    Fail(405, "method");
    Response.End();
}
string key = LoadKey();
if (string.IsNullOrEmpty(key))
{
    Fail(200, "missing_key");
    Response.End();
}
string body = HttpGet(TOKEN_URL, key);
string token = ExtractToken(body);
if (string.IsNullOrEmpty(token))
{
    Fail(502, "no_token");
    Response.End();
}
Response.Write("{\"ok\":true,\"token\":\"" + token.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"}");
%>
