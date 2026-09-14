<%@LANGUAGE="VBSCRIPT" CODEPAGE="65001"%>
<%
On Error Resume Next
Response.ContentType = "application/json"
Response.AddHeader "Access-Control-Allow-Origin", "*"
Response.AddHeader "Cache-Control", "no-store"

If Request.ServerVariables("REQUEST_METHOD") = "OPTIONS" Then
  Response.Status = "204 No Content"
  Response.End
End If

If Request.ServerVariables("REQUEST_METHOD") = "GET" Then
  Response.Write "{""ok"":true,""live"":true}"
  Response.End
End If

Dim fullMsg, appliancetype
appliancetype = Trim(Request.Form("appliancetype") & "")
If appliancetype = "" Then appliancetype = Trim(Request.Form("appliance") & "")
If appliancetype = "" Then appliancetype = Trim(Request.Form("appliance_type") & "")
If appliancetype = "" Then appliancetype = Trim(Request.Form("service") & "")
If appliancetype = "" Then appliancetype = "Not specified"
fullMsg = "New Booking: " & appliancetype & " - " & Request.Form("name") & vbCrLf & vbCrLf & "Name: " & Request.Form("name") & vbCrLf & "Phone: " & Request.Form("phone") & vbCrLf & "Email: " & Request.Form("email") & vbCrLf & "Postcode: " & Request.Form("postcode") & vbCrLf & "Appliance: " & appliancetype & vbCrLf & "Message: " & Request.Form("message") & vbCrLf & "Time: " & Now()
Dim ntfyHttp
Set ntfyHttp = Server.CreateObject("MSXML2.ServerXMLHTTP")
If Err.Number <> 0 Then
  Err.Clear
  Set ntfyHttp = Server.CreateObject("MSXML2.ServerXMLHTTP.6.0")
End If
If Not ntfyHttp Is Nothing Then
  ntfyHttp.setTimeouts 4000, 4000, 8000, 8000
  ntfyHttp.Open "POST", "https://ntfy.sh/cold-direct-bookings-221345", False
  ntfyHttp.setRequestHeader "Title", "New Booking! " & Request.Form("name")
  ntfyHttp.setRequestHeader "Priority", "high"
  ntfyHttp.setRequestHeader "Tags", "tada"
  ntfyHttp.Send fullMsg
End If
Set ntfyHttp = Nothing
Err.Clear
Dim mail
Set mail = Server.CreateObject("CDO.Message")
If Err.Number = 0 Then
  mail.From = "noreply@colddirect.co.uk"
  mail.To = "coldcom@hotmail.co.uk"
  mail.Subject = "New Booking: " & appliancetype & " - " & Request.Form("name")
  mail.TextBody = fullMsg
  mail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/sendusing") = 2
  mail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserver") = "localhost"
  mail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserverport") = 25
  mail.Configuration.Fields.Update
  mail.Send
End If
Set mail = Nothing
Err.Clear
Response.Write "{""ok"":true,""message"":""Thanks. We will contact you shortly.""}"
%>
