<%@LANGUAGE="VBSCRIPT" CODEPAGE="65001"%>
<%
' ColdDirect site maintenance API. Key required. No shell / eval.
On Error Resume Next
Response.Buffer = True
Response.Charset = "utf-8"
Response.ContentType = "text/plain"
Response.AddHeader "Cache-Control", "no-store"
Response.AddHeader "X-Content-Type-Options", "nosniff"

Const AGENT_KEY = "CD2026-SECURE"
Const MAX_BYTES = 1500000
Const SITE_HOST = "https://colddirect.co.uk/"

Function JsonEsc(s)
  Dim t
  t = s & ""
  t = Replace(t, "\", "\\")
  t = Replace(t, """", "\""")
  t = Replace(t, vbCrLf, "\n")
  t = Replace(t, vbCr, "\n")
  t = Replace(t, vbLf, "\n")
  t = Replace(t, Chr(9), "\t")
  JsonEsc = t
End Function

Sub Fail(code, msg)
  Response.Status = code
  Response.Write msg
  Response.End
End Sub

Sub OkJson(body)
  Response.Write "{""ok"":true," & body & "}"
  Response.End
End Sub

Function GetParam(n)
  Dim v
  v = Trim(Request.QueryString(n) & "")
  If v = "" Then v = Trim(Request.Form(n) & "")
  GetParam = v
End Function

Function IsoToday()
  Dim d
  d = Date()
  IsoToday = Year(d) & "-" & Right("0" & Month(d), 2) & "-" & Right("0" & Day(d), 2)
End Function

Function IsoStamp(dt)
  IsoStamp = Year(dt) & "-" & Right("0" & Month(dt), 2) & "-" & Right("0" & Day(dt), 2)
End Function

Function AllowedExt(path)
  Dim ext
  ext = LCase(Mid(path, InStrRev(path, ".") + 1))
  AllowedExt = (ext = "asp" Or ext = "html" Or ext = "htm" Or ext = "css" Or ext = "js" Or ext = "xml" Or ext = "txt" Or ext = "json")
End Function

Function SafeMap(rel)
  Dim root, full, fs, nRel
  nRel = Replace(rel & "", "\", "/")
  nRel = Replace(nRel, Chr(0), "")
  If Left(nRel, 1) = "/" Then nRel = Mid(nRel, 2)
  If InStr(nRel, "..") > 0 Or InStr(nRel, ":") > 0 Then
    SafeMap = ""
    Exit Function
  End If
  Set fs = Server.CreateObject("Scripting.FileSystemObject")
  root = fs.GetFolder(Server.MapPath("/")).Path
  If Len(nRel) = 0 Then
    full = root
  Else
    full = fs.BuildPath(root, Replace(nRel, "/", "\"))
  End If
  If LCase(Left(full, Len(root))) <> LCase(root) Then
    SafeMap = ""
    Exit Function
  End If
  SafeMap = full
End Function

Function SafeAspName(fname)
  Dim n, i, ch, ok, ext
  n = LCase(Trim(fname & ""))
  n = Replace(n, "\", "/")
  If InStr(n, "/") > 0 Then n = Mid(n, InStrRev(n, "/") + 1)
  If InStr(n, "..") > 0 Or InStr(n, ":") > 0 Or InStr(n, Chr(0)) > 0 Then
    SafeAspName = ""
    Exit Function
  End If
  If Len(n) < 5 Or Len(n) > 120 Then
    SafeAspName = ""
    Exit Function
  End If
  ext = LCase(Mid(n, InStrRev(n, ".")))
  If ext <> ".asp" Then
    SafeAspName = ""
    Exit Function
  End If
  ok = True
  For i = 1 To Len(n)
    ch = Mid(n, i, 1)
    If Not (ch >= "a" And ch <= "z") And Not (ch >= "0" And ch <= "9") And ch <> "-" And ch <> "_" And ch <> "." Then
      ok = False
      Exit For
    End If
  Next
  If ok Then
    SafeAspName = n
  Else
    SafeAspName = ""
  End If
End Function

Function RootPath()
  Dim fs
  Set fs = Server.CreateObject("Scripting.FileSystemObject")
  RootPath = fs.GetFolder(Server.MapPath("/")).Path
End Function

Sub WriteTextFile(fullPath, content)
  Dim fs, ts
  Set fs = Server.CreateObject("Scripting.FileSystemObject")
  Set ts = fs.OpenTextFile(fullPath, 2, True)
  ts.Write content
  ts.Close
End Sub

Function ReadTextFile(fullPath)
  Dim ts, fs
  Set fs = Server.CreateObject("Scripting.FileSystemObject")
  Set ts = fs.OpenTextFile(fullPath, 1, False)
  ReadTextFile = ts.ReadAll
  ts.Close
End Function

Sub EnsureSitemapUrl(fname)
  Dim fs, smPath, xml, loc, today, block
  Set fs = Server.CreateObject("Scripting.FileSystemObject")
  smPath = fs.BuildPath(RootPath(), "sitemap.xml")
  loc = SITE_HOST & fname
  today = IsoToday()
  If fs.FileExists(smPath) Then
    xml = ReadTextFile(smPath)
  Else
    xml = "<?xml version=""1.0"" encoding=""UTF-8""?>" & vbCrLf & "<urlset xmlns=""http://www.sitemaps.org/schemas/sitemap/0.9"">" & vbCrLf & "</urlset>"
  End If
  If InStr(1, xml, loc, vbTextCompare) > 0 Then Exit Sub
  If InStr(1, xml, "https://www.colddirect.co.uk/" & fname, vbTextCompare) > 0 Then Exit Sub
  block = "  <url>" & vbCrLf & "    <loc>" & loc & "</loc>" & vbCrLf & "    <lastmod>" & today & "</lastmod>" & vbCrLf & "  </url>" & vbCrLf
  If InStr(1, xml, "</urlset>", vbTextCompare) > 0 Then
    xml = Replace(xml, "</urlset>", block & "</urlset>", 1, 1, 0)
  Else
    xml = xml & vbCrLf & block & "</urlset>"
  End If
  WriteTextFile smPath, xml
End Sub

Function BuildCommercialSitemap()
  Dim fs, folder, file, xml, names, i, j, tmp, arr
  Set fs = Server.CreateObject("Scripting.FileSystemObject")
  Set folder = fs.GetFolder(RootPath())
  names = ""
  For Each file In folder.Files
    If LCase(fs.GetExtensionName(file.Name)) = "asp" Then
      If InStr(1, LCase(file.Name), "commercial-", vbTextCompare) > 0 Then
        If names <> "" Then names = names & "|"
        names = names & file.Name
      End If
    End If
  Next
  xml = "<?xml version=""1.0"" encoding=""UTF-8""?>" & vbCrLf
  xml = xml & "<urlset xmlns=""http://www.sitemaps.org/schemas/sitemap/0.9"">" & vbCrLf
  If names <> "" Then
    arr = Split(names, "|")
    For i = 0 To UBound(arr)
      For j = i + 1 To UBound(arr)
        If LCase(arr(j)) < LCase(arr(i)) Then
          tmp = arr(i): arr(i) = arr(j): arr(j) = tmp
        End If
      Next
    Next
    For i = 0 To UBound(arr)
      xml = xml & "  <url>" & vbCrLf
      xml = xml & "    <loc>" & SITE_HOST & arr(i) & "</loc>" & vbCrLf
      xml = xml & "    <lastmod>" & IsoToday() & "</lastmod>" & vbCrLf
      xml = xml & "  </url>" & vbCrLf
    Next
  End If
  xml = xml & "</urlset>" & vbCrLf
  BuildCommercialSitemap = xml
End Function

Dim supplied, action, fso
Dim folder, file, html, changed, hits, n, oldBrand, newBrand, splitOld, splitNew
Dim q, matches, mcount, f2, t2, c2
Dim rpath, rfull, wpath, wfull, body, names, f3
Dim fname, htmlBody, dest, pleskDir, pleskDest
Dim smXml, smPath, totalFiles, commercialPages, lastMod, f4, lm

supplied = GetParam("k")
If supplied = "" Then supplied = GetParam("key")
If supplied <> AGENT_KEY Then Fail "403 Forbidden", "forbidden"

action = LCase(GetParam("a"))
If action = "" Then action = LCase(GetParam("action"))
If action = "" Then action = "ping"

Set fso = Server.CreateObject("Scripting.FileSystemObject")

If action = "ping" Then
  Response.Write "READY v3"
  Response.End
End If

If action = "replace_branding" Then
  oldBrand = "Cold" & "line"
  newBrand = "Cold" & "Direct"
  splitOld = "Cold" & "<span>line</span>"
  splitNew = "Cold" & "<span>Direct</span>"
  changed = 0
  hits = 0
  Set folder = fso.GetFolder(RootPath())
  For Each file In folder.Files
    If LCase(fso.GetExtensionName(file.Name)) = "asp" And LCase(file.Name) <> "cold-agent-v3.asp" Then
      html = ReadTextFile(file.Path)
      n = 0
      If InStr(html, splitOld) > 0 Then
        n = n + (Len(html) - Len(Replace(html, splitOld, ""))) \ Len(splitOld)
        html = Replace(html, splitOld, splitNew)
      End If
      If InStr(html, oldBrand) > 0 Then
        n = n + (Len(html) - Len(Replace(html, oldBrand, ""))) \ Len(oldBrand)
        html = Replace(html, oldBrand, newBrand)
      End If
      If n > 0 Then
        WriteTextFile file.Path, html
        changed = changed + 1
        hits = hits + n
      End If
    End If
  Next
  OkJson """replacedFiles"":" & changed & ",""hits"":" & hits & ",""from"":""" & JsonEsc(oldBrand) & """,""to"":""" & JsonEsc(newBrand) & """"
End If

If action = "find" Then
  q = GetParam("q")
  If q = "" Then q = "Cold" & "line"
  matches = ""
  mcount = 0
  Set folder = fso.GetFolder(RootPath())
  For Each f2 In folder.Files
    If LCase(fso.GetExtensionName(f2.Name)) = "asp" Then
      t2 = ReadTextFile(f2.Path)
      c2 = 0
      If Len(q) > 0 Then c2 = (Len(t2) - Len(Replace(t2, q, ""))) \ Len(q)
      If c2 > 0 Then
        If matches <> "" Then matches = matches & ","
        matches = matches & "{""file"":""" & JsonEsc(f2.Name) & """,""hits"":" & c2 & "}"
        mcount = mcount + 1
      End If
    End If
  Next
  OkJson """query"":""" & JsonEsc(q) & """,""files"":" & mcount & ",""matches"":[" & matches & "]"
End If

If action = "read" Then
  rpath = GetParam("path")
  rfull = SafeMap(rpath)
  If rfull = "" Or Not AllowedExt(rfull) Then Fail "400 Bad Request", "invalid path"
  If Not fso.FileExists(rfull) Then Fail "404 Not Found", "not found"
  If fso.GetFile(rfull).Size > MAX_BYTES Then Fail "413 Payload Too Large", "too large"
  html = ReadTextFile(rfull)
  OkJson """path"":""" & JsonEsc(rpath) & """,""content"":""" & JsonEsc(html) & """"
End If

If action = "write" Then
  wpath = GetParam("path")
  body = Request.Form("content")
  If body = "" Then body = Request.Form("html")
  wfull = SafeMap(wpath)
  If wfull = "" Or Not AllowedExt(wfull) Then Fail "400 Bad Request", "invalid path"
  If Len(body) = 0 Then Fail "400 Bad Request", "missing content"
  If Len(body) > MAX_BYTES Then Fail "413 Payload Too Large", "too large"
  WriteTextFile wfull, body
  OkJson """path"":""" & JsonEsc(wpath) & """,""bytes"":" & Len(body)
End If

If action = "list" Then
  names = ""
  Set folder = fso.GetFolder(RootPath())
  For Each f3 In folder.Files
    If LCase(fso.GetExtensionName(f3.Name)) = "asp" Then
      If names <> "" Then names = names & ","
      names = names & """" & JsonEsc(f3.Name) & """"
    End If
  Next
  OkJson """files"":[" & names & "]"
End If

If action = "create" Then
  fname = SafeAspName(GetParam("f"))
  If fname = "" Then Fail "400 Bad Request", "invalid filename"
  htmlBody = Request.Form("html")
  If Len(htmlBody) = 0 Then htmlBody = Request("html")
  If Len(htmlBody) = 0 Then Fail "400 Bad Request", "missing html"
  If Len(htmlBody) > MAX_BYTES Then Fail "413 Payload Too Large", "too large"
  dest = fso.BuildPath(RootPath(), fname)
  WriteTextFile dest, htmlBody
  pleskDir = fso.BuildPath(RootPath(), "plesk-upload")
  If fso.FolderExists(pleskDir) Then
    pleskDest = fso.BuildPath(pleskDir, fname)
    WriteTextFile pleskDest, htmlBody
  End If
  EnsureSitemapUrl fname
  Response.Write "CREATED:" & fname
  Response.End
End If

If action = "sitemap" Then
  smXml = BuildCommercialSitemap()
  smPath = fso.BuildPath(RootPath(), "sitemap.xml")
  WriteTextFile smPath, smXml
  Response.Write smXml
  Response.End
End If

If action = "stats" Then
  totalFiles = 0
  commercialPages = 0
  lastMod = ""
  Set folder = fso.GetFolder(RootPath())
  For Each f4 In folder.Files
    totalFiles = totalFiles + 1
    If LCase(fso.GetExtensionName(f4.Name)) = "asp" Then
      If InStr(1, LCase(f4.Name), "commercial-", vbTextCompare) > 0 Then
        commercialPages = commercialPages + 1
      End If
    End If
    lm = IsoStamp(f4.DateLastModified)
    If lastMod = "" Or lm > lastMod Then lastMod = lm
  Next
  Response.Write "{""total_files"":" & totalFiles & ",""commercial_pages"":" & commercialPages & ",""last_modified"":""" & lastMod & """}"
  Response.End
End If

Fail "400 Bad Request", "unknown action"
%>
