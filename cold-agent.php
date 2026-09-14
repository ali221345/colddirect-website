<?php
$KEY = "Cold2025";
if (($_GET['key'] ?? '') !== $KEY) { http_response_code(403); die("Forbidden - wrong key"); }
$action = $_POST['action'] ?? $_GET['action'] ?? '';
if ($action === '' && !isset($_POST['slug'])) { echo "✅ ColdDirect Agent Ready - key OK"; exit; }
if ($action === 'create_page' || isset($_POST['slug'])) {
  $slug = preg_replace('/[^a-z0-9-]/','', strtolower($_POST['slug'] ?? ''));
  $html = $_POST['html'] ?? '';
  if (!$slug || !$html) die("missing slug/html");
  $dir = __DIR__ . "/$slug";
  if (!is_dir($dir)) mkdir($dir, 0777, true);
  file_put_contents($dir . "/index.html", $html);
  echo "OK created /$slug/"; exit;
}
echo "✅ ColdDirect Agent Ready";
