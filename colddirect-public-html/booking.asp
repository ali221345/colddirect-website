<%@LANGUAGE="VBSCRIPT" CODEPAGE="65001"%>
<%
On Error Resume Next
Response.ContentType = "application/json"
Response.Charset = "utf-8"
Response.AddHeader "Cache-Control", "no-store"
Response.AddHeader "Access-Control-Allow-Origin", "*"

If Request.ServerVariables("REQUEST_METHOD") = "OPTIONS" Then
  Response.Status = "204 No Content"
  Response.End
End If

If Request.ServerVariables("REQUEST_METHOD") = "GET" Then
  Response.Write "{""ok"":true,""live"":true}"
  Response.End
End If

Function Clean(v, maxLen)
  Dim s
  s = Trim(CStr(v & ""))
  s = Replace(s, vbCr, " ")
  s = Replace(s, vbLf, " ")
  If Len(s) > maxLen Then s = Left(s, maxLen)
  Clean = s
End Function

Dim name, phone, email, service, message, page, website
name = Clean(Request.Form("name"), 120)
phone = Clean(Request.Form("phone"), 40)
email = Clean(Request.Form("email"), 120)
service = Clean(Request.Form("service"), 120)
message = Clean(Request.Form("message"), 4000)
page = Clean(Request.Form("page"), 200)
website = Clean(Request.Form("website"), 80)

If website <> "" Then
  Response.Write "{""ok"":true,""message"":""We will call you shortly on 07983 759320""}"
  Response.End
End If

If name = "" Or phone = "" Or email = "" Then
  Response.Status = "400 Bad Request"
  Response.Write "{""ok"":false,""error"":""Name, phone and email are required.""}"
  Response.End
End If

Dim fullMsg
fullMsg = "New consultation booking from colddirect.co.uk" & vbCrLf & vbCrLf _
  & "Name: " & name & vbCrLf _
  & "Phone: " & phone & vbCrLf _
  & "Email: " & email & vbCrLf _
  & "Service: " & service & vbCrLf _
  & "Message: " & message & vbCrLf _
  & "Page: " & page & vbCrLf _
  & "Time: " & Now()

Dim fso, logFile, logPath, jsonPath, jsonF
Set fso = Server.CreateObject("Scripting.FileSystemObject")
If Err.Number <> 0 Then Err.Clear
If Not fso Is Nothing Then
  logPath = Server.MapPath("/bookings")
  If Not fso.FolderExists(logPath) Then fso.CreateFolder(logPath)
  Err.Clear
  Set logFile = fso.OpenTextFile(logPath & "\booking-log.txt", 8, True)
  If Err.Number = 0 Then
    logFile.WriteLine Now() & vbTab & name & vbTab & phone & vbTab & email & vbTab & message
    logFile.Close
  End If
  Err.Clear
  Set jsonF = fso.OpenTextFile(logPath & "\bookings.json", 8, True)
  If Err.Number = 0 Then
    jsonF.WriteLine "{""time"":""" & Now() & """,""name"":""" & Replace(name, """", "'") & """,""phone"":""" & phone & """,""email"":""" & email & """},"
    jsonF.Close
  End If
End If
Set logFile = Nothing
Set jsonF = Nothing
Set fso = Nothing
Err.Clear

Dim ntfyHttp
Set ntfyHttp = Server.CreateObject("MSXML2.ServerXMLHTTP")
If Err.Number <> 0 Then
  Err.Clear
  Set ntfyHttp = Server.CreateObject("MSXML2.ServerXMLHTTP.6.0")
End If
If Not ntfyHttp Is Nothing Then
  ntfyHttp.setTimeouts 4000, 4000, 8000, 8000
  ntfyHttp.Open "POST", "https://ntfy.sh/cold-direct-bookings-221345", False
  ntfyHttp.setRequestHeader "Title", "New Booking! " & name
  ntfyHttp.setRequestHeader "Priority", "high"
  ntfyHttp.setRequestHeader "Tags", "envelope"
  ntfyHttp.Send fullMsg
End If
Set ntfyHttp = Nothing
Err.Clear

Dim mail
Set mail = Server.CreateObject("CDO.Message")
If Err.Number = 0 Then
  mail.From = "noreply@colddirect.co.uk"
  mail.To = "coldcom@hotmail.co.uk"
  mail.Subject = "New Booking from Website - " & name
  mail.TextBody = fullMsg
  mail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/sendusing") = 2
  mail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserver") = "localhost"
  mail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserverport") = 25
  mail.Configuration.Fields.Update
  mail.Send
End If
Set mail = Nothing
Err.Clear

Response.Write "{""ok"":true,""message"":""We will call you shortly on 07983 759320""}"
%>
