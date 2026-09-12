<?php
// /httpdocs/daily-job.php — Plesk scheduled task, once a day
header('Content-Type: text/plain; charset=utf-8');

$logFile = __DIR__ . '/agent-daily.log';
$time = date('Y-m-d H:i:s');
file_put_contents($logFile, "[$time] Daily job started\n", FILE_APPEND);

$imagesDir = __DIR__ . '/images';
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

$ok = 0;
$missing = array();
foreach ($check as $name) {
  $path = $imagesDir . '/' . $name;
  if (is_file($path)) {
    $ok++;
    file_put_contents($logFile, "[$time] OK $name " . filesize($path) . " bytes\n", FILE_APPEND);
  } else {
    $missing[] = $name;
    file_put_contents($logFile, "[$time] MISSING $name\n", FILE_APPEND);
  }
}

file_put_contents(
  $logFile,
  "[$time] Daily job finished — $ok present, " . count($missing) . " missing\n",
  FILE_APPEND
);

echo "OK $time images=$ok missing=" . count($missing);
