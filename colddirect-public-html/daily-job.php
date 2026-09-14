<?php
date_default_timezone_set('Europe/London');
header('Content-Type: text/plain; charset=utf-8');
$logFile = __DIR__ . '/agent-daily.log';
$time = date('Y-m-d H:i:s');
file_put_contents($logFile, "[$time] Daily job started\n", FILE_APPEND);

$imagesDir = __DIR__ . '/images';
$restoreDir = $imagesDir . '/_restore';
$githubBase = 'https://raw.githubusercontent.com/ali221345/colddirect-website/main/colddirect-public-html/images/';

$check = array(
  'homepage-hero-chiller.webp',
  'commercial-fridge-north-london.webp',
  'commercial-freezer-repair-london.webp',
  'empire-fridge.webp',
  'bottle-cooler.webp',
  'polar-fridge.webp',
  'sub-zero-fridge.webp',
  'williams-fridge.webp',
  'adexa-fridge.webp',
  'wine-cooler.webp',
);

$aliases = array(
  'homepage-hero-chiller.webp' => array(
    'cold-room-repair-london.webp',
    'homepage/cold-room.webp',
    'brands/cold-room-chiller-repair.webp',
  ),
  'commercial-fridge-north-london.webp' => array(
    'commercial-fridge-repair-london.webp',
    'homepage/commercial-fridge.webp',
    'brands/commercial-fridge.webp',
  ),
  'commercial-freezer-repair-london.webp' => array(
    'freezer_engineers_repair.webp',
    'homepage/freezer-room.webp',
    'brands/commercial-freezer.webp',
  ),
  'empire-fridge.webp' => array(
    'brands/empire-fridge.webp',
    'homepage/empire-display.webp',
    'empire-fridge-repair.webp',
  ),
  'bottle-cooler.webp' => array(
    'brands/bottle-cooler.webp',
    'homepage/bottle-cooler.webp',
  ),
  'polar-fridge.webp' => array(
    'brands/polar-fridge.webp',
    'homepage/polar-fridge.webp',
  ),
  'sub-zero-fridge.webp' => array(
    'homepage/sub-zero-fridge.webp',
    'sub-zero-fridge-repair.webp',
  ),
  'williams-fridge.webp' => array(
    'brands/williams-fridge.webp',
    'homepage/williams-fridge.webp',
  ),
  'adexa-fridge.webp' => array(
    'brands/adexa-fridge.webp',
    'homepage/adexa-fridge.webp',
  ),
  'wine-cooler.webp' => array(
    'brands/wine-fridge.webp',
    'dual_zone_wine_cooler.webp',
  ),
);

function cd_http_get($url)
{
  if (function_exists('curl_init')) {
    $ch = curl_init($url);
    curl_setopt_array($ch, array(
      CURLOPT_RETURNTRANSFER => true,
      CURLOPT_FOLLOWLOCATION => true,
      CURLOPT_CONNECTTIMEOUT => 15,
      CURLOPT_TIMEOUT => 45,
      CURLOPT_USERAGENT => 'ColdDirect-DailyJob/1.0',
    ));
    $body = curl_exec($ch);
    $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($code >= 200 && $code < 300 && $body !== false && strlen($body) > 1000) {
      return $body;
    }
    return false;
  }
  $ctx = stream_context_create(array(
    'http' => array('timeout' => 45, 'follow_location' => 1, 'user_agent' => 'ColdDirect-DailyJob/1.0'),
    'ssl' => array('verify_peer' => true, 'verify_peer_name' => true),
  ));
  $body = @file_get_contents($url, false, $ctx);
  if ($body !== false && strlen($body) > 1000) {
    return $body;
  }
  return false;
}

function cd_brand_token($filename)
{
  $name = strtolower(basename(str_replace('\\', '/', $filename)));
  $brands = array('williams', 'foster', 'true', 'gram', 'polar', 'blizzard', 'adexa', 'empire', 'hoshizaki', 'sub-zero', 'subzero');
  usort($brands, function ($a, $b) {
    return strlen($b) - strlen($a);
  });
  foreach ($brands as $b) {
    if (strpos($name, $b) !== false) {
      if ($b === 'subzero' || $b === 'sub-zero') {
        return 'sub-zero';
      }
      return $b;
    }
  }
  return '';
}

function cd_brands_compatible($destName, $srcPath)
{
  $d = cd_brand_token($destName);
  $s = cd_brand_token($srcPath);
  if ($d === '' || $s === '') {
    return true;
  }
  return $d === $s;
}

function cd_restore_image($name, $dest, $restoreDir, $imagesDir, $aliases, $githubBase, $logFile, $time)
{
  $sources = array();
  $backup = $restoreDir . '/' . $name;
  if (is_file($backup)) {
    $sources[] = $backup;
  }
  if (!empty($aliases[$name])) {
    foreach ($aliases[$name] as $rel) {
      $sources[] = $imagesDir . '/' . $rel;
    }
  }

  foreach ($sources as $src) {
    if (!is_file($src) || filesize($src) < 1000) {
      continue;
    }
    if (!cd_brands_compatible($name, $src)) {
      file_put_contents(
        $logFile,
        "[$time] SKIP_BRAND_MISMATCH will not copy " . basename($src) . " onto $name\n",
        FILE_APPEND
      );
      continue;
    }
    if (@copy($src, $dest)) {
      @chmod($dest, 0644);
      file_put_contents(
        $logFile,
        "[$time] RESTORED $name from " . basename(dirname($src)) . '/' . basename($src) . " - " . filesize($dest) . " bytes\n",
        FILE_APPEND
      );
      return true;
    }
  }

  if (!cd_brands_compatible($name, $githubBase . $name)) {
    file_put_contents($logFile, "[$time] SKIP_BRAND_MISMATCH GitHub URL for $name\n", FILE_APPEND);
    file_put_contents($logFile, "[$time] RESTORE_FAILED $name\n", FILE_APPEND);
    return false;
  }

  $remote = cd_http_get($githubBase . rawurlencode($name));
  if ($remote !== false) {
    if (@file_put_contents($dest, $remote) !== false) {
      @chmod($dest, 0644);
      file_put_contents(
        $logFile,
        "[$time] RESTORED $name from GitHub - " . filesize($dest) . " bytes\n",
        FILE_APPEND
      );
      return true;
    }
  }

  file_put_contents($logFile, "[$time] RESTORE_FAILED $name\n", FILE_APPEND);
  return false;
}

if (!is_dir($imagesDir)) {
  @mkdir($imagesDir, 0755, true);
}

$ok = 0;
$missing = 0;
$restored = 0;
foreach ($check as $name) {
  $path = $imagesDir . '/' . $name;
  if (is_file($path) && filesize($path) > 1000) {
    $ok++;
    file_put_contents($logFile, "[$time] OK $name - " . filesize($path) . " bytes\n", FILE_APPEND);
    continue;
  }
  file_put_contents($logFile, "[$time] MISSING $name — restoring\n", FILE_APPEND);
  if (cd_restore_image($name, $path, $restoreDir, $imagesDir, $aliases, $githubBase, $logFile, $time)) {
    $ok++;
    $restored++;
  } else {
    $missing++;
  }
}

file_put_contents(
  $logFile,
  "[$time] Daily job finished - $ok present, $missing missing, $restored restored\n",
  FILE_APPEND
);
echo "OK $time images=$ok missing=$missing restored=$restored";
