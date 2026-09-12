<?php
date_default_timezone_set('Europe/London');
header('Content-Type: text/plain; charset=utf-8');
$logFile = __DIR__ . '/keepalive.log';
$time = date('Y-m-d H:i:s');

$urls = array(
  'https://www.colddirect.co.uk/',
  'https://colddirect.co.uk/',
  'https://www.colddirect.co.uk/images/homepage-hero-chiller.webp',
  'https://www.colddirect.co.uk/images/commercial-fridge-north-london.webp',
  'https://www.colddirect.co.uk/images/commercial-freezer-repair-london.webp',
  'https://www.colddirect.co.uk/images/empire-fridge.webp',
  'https://www.colddirect.co.uk/images/bottle-cooler.webp',
  'https://www.colddirect.co.uk/images/polar-fridge.webp',
  'https://www.colddirect.co.uk/images/sub-zero-fridge.webp',
  'https://www.colddirect.co.uk/images/williams-fridge.webp',
  'https://www.colddirect.co.uk/images/adexa-fridge.webp',
  'https://www.colddirect.co.uk/images/wine-cooler.webp',
);

function cd_ping($url)
{
  if (function_exists('curl_init')) {
    $ch = curl_init($url);
    curl_setopt_array($ch, array(
      CURLOPT_RETURNTRANSFER => true,
      CURLOPT_FOLLOWLOCATION => true,
      CURLOPT_CONNECTTIMEOUT => 10,
      CURLOPT_TIMEOUT => 20,
      CURLOPT_USERAGENT => 'ColdDirect-KeepAlive/1.0',
    ));
    $body = curl_exec($ch);
    $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $err = curl_error($ch);
    curl_close($ch);
    return array($code, $body === false ? 0 : strlen($body), $err);
  }
  $ctx = stream_context_create(array(
    'http' => array('timeout' => 20, 'follow_location' => 1, 'user_agent' => 'ColdDirect-KeepAlive/1.0'),
    'ssl' => array('verify_peer' => true, 'verify_peer_name' => true),
  ));
  $body = @file_get_contents($url, false, $ctx);
  $code = 0;
  if (isset($http_response_header[0]) && preg_match('/\s(\d{3})\s/', $http_response_header[0], $m)) {
    $code = (int) $m[1];
  } elseif ($body !== false) {
    $code = 200;
  }
  return array($code, $body === false ? 0 : strlen($body), $body === false ? 'fetch failed' : '');
}

file_put_contents($logFile, "[$time] Keepalive started\n", FILE_APPEND);
$ok = 0;
$bad = 0;
foreach ($urls as $url) {
  list($code, $bytes, $err) = cd_ping($url);
  if ($code >= 200 && $code < 400) {
    $ok++;
    file_put_contents($logFile, "[$time] OK $code $bytes $url\n", FILE_APPEND);
  } else {
    $bad++;
    file_put_contents($logFile, "[$time] FAIL $code $err $url\n", FILE_APPEND);
  }
}
file_put_contents($logFile, "[$time] Keepalive finished ok=$ok fail=$bad\n", FILE_APPEND);
echo "OK $time warmup=$ok fail=$bad";
