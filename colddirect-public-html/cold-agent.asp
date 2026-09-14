<%
KEY="COLD2025"
If Request.QueryString("key")<>KEY Then Response.Write "forbidden": Response.End
action = Request.QueryString("action")
If action="deploy_white_design_2026_05_13" Then
 Set fso = Server.CreateObject("Scripting.FileSystemObject")
 templatePath = Server.MapPath("/commercial-fridge-repair-london.asp")
 If Not fso.FileExists(templatePath) Then Response.Write "Template not found": Response.End
 Set ts = fso.OpenTextFile(templatePath,1): tc = ts.ReadAll: ts.Close
 tc = Replace(tc, "0208 123 4667", "07983 759320")
 tc = Replace(tc, "02081234667", "07983759320")
 tc = Replace(tc, "0208 123 4567", "0203 952 4822")
 brands = Array("beko","bosch","samsung","hotpoint","lg","miele","neff","siemens","zanussi","aeg","indesit","whirlpool")
 For i=0 To UBound(brands)
  b=brands(i): Bcap=UCase(Left(b,1))&Mid(b,2): slug=b&"-fridge-repair-london.asp"
  html = tc
  html = Replace(html, "Commercial Fridge Repair London", Bcap & " Fridge Repair London", 1, -1, 1)
  html = Replace(html, "commercial fridge repair", Bcap & " fridge repair", 1, -1, 1)
  html = Replace(html, "Commercial Fridge", Bcap & " Fridge", 1, -1, 1)
  html = Replace(html, "commercial fridge", Bcap & " fridge", 1, -1, 1)
  Set f = fso.CreateTextFile(Server.MapPath("/"&slug), True): f.Write html: f.Close
  Response.Write "OK WHITE "&slug&"<br>"
 Next
 Response.Write "Deployed 12 WHITE DESIGN"
 Response.End
End If
If action="cleanup_defunct_2026_05_13" Then
 Set fso = Server.CreateObject("Scripting.FileSystemObject")
 folders = Array("blog","book","brandsfoster","colddirect-public-html","mnt")
 For i=0 To UBound(folders)
  p=Server.MapPath("/"&folders(i))
  If fso.FolderExists(p) Then
   fso.DeleteFolder p, True
   Response.Write "Deleted "&folders(i)&"<br>"
  Else
   Response.Write "Not found "&folders(i)&"<br>"
  End If
 Next
 Response.End
End If
Response.Write "Ready"
%>
