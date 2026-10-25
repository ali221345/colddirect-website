<%@ Page Language="C#" %>
<%@ Import Namespace="System.IO" %>
<script runat="server">
protected void Page_Load(object sender, EventArgs e)
{
    Response.ContentType = "application/json; charset=utf-8";
    Response.AddHeader("Cache-Control", "no-store");
    string key = "";
    try
    {
        string path = Server.MapPath("~/App_Data/vapi-public.key");
        if (File.Exists(path)) key = File.ReadAllText(path).Trim();
    }
    catch { }
    key = key.Replace("\\", "\\\\").Replace("\"", "\\\"");
    Response.Write("{\"ok\":true,\"assistantId\":\"e31c40c7-a45b-4dff-833c-320c54250743\",\"publicKey\":\"" + key + "\"}");
}
</script>
