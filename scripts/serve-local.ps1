$root = Split-Path -Parent $PSScriptRoot
$prefix = "http://127.0.0.1:8765/"
$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add($prefix)
$listener.Start()
Write-Output "serving $root on $prefix"
$mimes = @{
  ".html"="text/html; charset=utf-8"; ".css"="text/css"; ".js"="application/javascript"
  ".png"="image/png"; ".jpg"="image/jpeg"; ".jpeg"="image/jpeg"; ".ico"="image/x-icon"
  ".xml"="application/xml"; ".svg"="image/svg+xml"; ".woff2"="font/woff2"
}
while ($listener.IsListening) {
  $ctx = $listener.GetContext()
  $rel = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath.TrimStart("/"))
  if ([string]::IsNullOrWhiteSpace($rel)) { $rel = "index.html" }
  $path = [IO.Path]::GetFullPath((Join-Path $root $rel))
  if (-not $path.StartsWith($root, [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path $path -PathType Leaf)) {
    $ctx.Response.StatusCode = 404
    $buf = [Text.Encoding]::UTF8.GetBytes("Not found")
    $ctx.Response.OutputStream.Write($buf, 0, $buf.Length)
    $ctx.Response.Close()
    continue
  }
  $ext = [IO.Path]::GetExtension($path).ToLowerInvariant()
  $ctx.Response.ContentType = $(if ($mimes.ContainsKey($ext)) { $mimes[$ext] } else { "application/octet-stream" })
  $bytes = [IO.File]::ReadAllBytes($path)
  $ctx.Response.ContentLength64 = $bytes.Length
  $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  $ctx.Response.Close()
}
