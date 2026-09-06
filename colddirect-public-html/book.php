<?php
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  http_response_code(405);
  echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
  exit;
}

$configFile = __DIR__ . '/booking-config.php';
$config = is_file($configFile) ? require $configFile : [];
$to = $config['to_email'] ?? 'coldcom@hotmail.co.uk';
$fromEmail = $config['from_email'] ?? 'noreply@colddirect.co.uk';
$fromName = $config['from_name'] ?? 'Cold Direct Website';
$resendKey = trim((string) ($config['resend_api_key'] ?? ''));
$webhook = trim((string) ($config['webhook_url'] ?? ''));

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
  $data = $_POST;
}

$honeypot = trim((string) ($data['website'] ?? ''));
if ($honeypot !== '') {
  echo json_encode(['ok' => true]);
  exit;
}

$name = trim((string) ($data['name'] ?? ''));
$phone = trim((string) ($data['phone'] ?? ''));
$email = trim((string) ($data['email'] ?? ''));
$date = trim((string) ($data['date'] ?? ''));
$message = trim((string) ($data['message'] ?? ''));
$page = trim((string) ($data['page'] ?? ''));

if ($name === '' || $phone === '' || $email === '') {
  http_response_code(400);
  echo json_encode(['ok' => false, 'error' => 'Name, phone and email are required.']);
  exit;
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
  http_response_code(400);
  echo json_encode(['ok' => false, 'error' => 'Enter a valid email address.']);
  exit;
}

$name = substr(strip_tags($name), 0, 120);
$phone = substr(strip_tags($phone), 0, 40);
$date = substr(strip_tags($date), 0, 40);
$message = substr(strip_tags($message), 0, 4000);
$page = substr(strip_tags($page), 0, 200);

$subject = 'New Booking from Website - ' . $name;
$body = "New consultation booking from colddirect.co.uk\n\n"
  . "Name: {$name}\n"
  . "Phone: {$phone}\n"
  . "Email: {$email}\n"
  . "Preferred date: " . ($date !== '' ? $date : '(not given)') . "\n"
  . "Message / product interest:\n{$message}\n\n"
  . "Page: {$page}\n"
  . "Time: " . gmdate('Y-m-d H:i:s') . " UTC\n";

$sent = false;
$error = '';

if ($resendKey !== '') {
  $payload = json_encode([
    'from' => $fromName . ' <' . $fromEmail . '>',
    'to' => [$to],
    'reply_to' => $email,
    'subject' => $subject,
    'text' => $body,
  ]);
  $ch = curl_init('https://api.resend.com/emails');
  curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => [
      'Authorization: Bearer ' . $resendKey,
      'Content-Type: application/json',
    ],
    CURLOPT_POSTFIELDS => $payload,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 15,
  ]);
  $res = curl_exec($ch);
  $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
  curl_close($ch);
  $sent = $code >= 200 && $code < 300;
  if (!$sent) {
    $error = 'Resend failed';
  }
} else {
  $headers = [];
  $headers[] = 'MIME-Version: 1.0';
  $headers[] = 'Content-Type: text/plain; charset=UTF-8';
  $headers[] = 'From: ' . $fromName . ' <' . $fromEmail . '>';
  $headers[] = 'Reply-To: ' . $email;
  $headers[] = 'X-Priority: 1';
  $headers[] = 'Importance: High';
  $encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
  $sent = @mail($to, $encodedSubject, $body, implode("\r\n", $headers));
  if (!$sent) {
    $error = 'Mail function failed';
  }
}

if ($webhook !== '') {
  $ch = curl_init($webhook);
  $isNtfy = stripos($webhook, 'ntfy.sh') !== false;
  if ($isNtfy) {
    curl_setopt_array($ch, [
      CURLOPT_POST => true,
      CURLOPT_HTTPHEADER => [
        'Title: New booking - ' . $name,
        'Priority: high',
        'Tags: envelope',
      ],
      CURLOPT_POSTFIELDS => $body,
      CURLOPT_RETURNTRANSFER => true,
      CURLOPT_TIMEOUT => 8,
    ]);
  } else {
    curl_setopt_array($ch, [
      CURLOPT_POST => true,
      CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
      CURLOPT_POSTFIELDS => json_encode([
        'event' => 'booking',
        'name' => $name,
        'phone' => $phone,
        'email' => $email,
        'date' => $date,
        'message' => $message,
        'page' => $page,
        'subject' => $subject,
      ]),
      CURLOPT_RETURNTRANSFER => true,
      CURLOPT_TIMEOUT => 8,
    ]);
  }
  curl_exec($ch);
  curl_close($ch);
}

if (!$sent) {
  http_response_code(500);
  echo json_encode(['ok' => false, 'error' => $error !== '' ? $error : 'Could not send booking.']);
  exit;
}

echo json_encode(['ok' => true]);
