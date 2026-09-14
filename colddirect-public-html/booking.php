<?php
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

$success = [
  'ok' => true,
  'message' => 'We will call you shortly on 07983 759320',
];

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
$smtpHost = trim((string) ($config['smtp_host'] ?? 'localhost'));
$smtpPort = (int) ($config['smtp_port'] ?? 25);
$smtpUser = trim((string) ($config['smtp_user'] ?? ''));
$smtpPass = (string) ($config['smtp_pass'] ?? '');

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
  $data = $_POST;
}

$honeypot = trim((string) ($data['website'] ?? ''));
if ($honeypot !== '') {
  echo json_encode($success);
  exit;
}

$name = trim((string) ($data['name'] ?? ''));
$phone = trim((string) ($data['phone'] ?? ''));
$email = trim((string) ($data['email'] ?? ''));
$service = trim((string) ($data['service'] ?? ''));
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
$service = substr(strip_tags($service), 0, 120);
$message = substr(strip_tags($message), 0, 4000);
$page = substr(strip_tags($page), 0, 200);

$subject = 'New Booking from Website - ' . $name;
$body = "New consultation booking from colddirect.co.uk\n\n"
  . "Name: {$name}\n"
  . "Phone: {$phone}\n"
  . "Email: {$email}\n"
  . "Service: " . ($service !== '' ? $service : '(not given)') . "\n"
  . "Message / product interest:\n{$message}\n\n"
  . "Page: {$page}\n"
  . "Time: " . gmdate('Y-m-d H:i:s') . " UTC\n";

$record = [
  'time' => gmdate('c'),
  'name' => $name,
  'phone' => $phone,
  'email' => $email,
  'service' => $service,
  'message' => $message,
  'page' => $page,
];

$logDir = __DIR__ . '/bookings';
if (!is_dir($logDir)) {
  @mkdir($logDir, 0755, true);
}
$logged = false;
if (is_dir($logDir) && is_writable($logDir)) {
  $logged = @file_put_contents(
    $logDir . '/booking-log.txt',
    gmdate('c') . "\t" . json_encode($record, JSON_UNESCAPED_UNICODE) . "\n",
    FILE_APPEND | LOCK_EX
  ) !== false;
  $jsonFile = $logDir . '/bookings.json';
  $list = [];
  if (is_file($jsonFile)) {
    $existing = json_decode((string) file_get_contents($jsonFile), true);
    if (is_array($existing)) {
      $list = $existing;
    }
  }
  $list[] = $record;
  @file_put_contents(
    $jsonFile,
    json_encode($list, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE),
    LOCK_EX
  );
}

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
  $cerr = curl_error($ch);
  curl_close($ch);
  $sent = $code >= 200 && $code < 300;
  if (!$sent) {
    $error = 'Resend failed HTTP ' . $code . ' ' . $cerr . ' ' . substr((string) $res, 0, 200);
    error_log('booking.php ' . $error);
  }
}

if (!$sent) {
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
    $error = 'mail() failed';
    error_log('booking.php mail() failed for ' . $email);
  }
}

if (!$sent) {
  $sent = cd_smtp_send($smtpHost, $smtpPort, $smtpUser, $smtpPass, $to, $fromEmail, $fromName, $email, $subject, $body);
  if (!$sent) {
    error_log('booking.php SMTP failed host=' . $smtpHost);
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
      CURLOPT_POSTFIELDS => json_encode($record),
      CURLOPT_RETURNTRANSFER => true,
      CURLOPT_TIMEOUT => 8,
    ]);
  }
  curl_exec($ch);
  curl_close($ch);
}

if (!$sent) {
  error_log('booking.php email not sent; logged=' . ($logged ? '1' : '0'));
}

echo json_encode($success);
exit;

function cd_smtp_expect($fp, $codes) {
  $line = '';
  while (!feof($fp)) {
    $chunk = fgets($fp, 515);
    if ($chunk === false) {
      break;
    }
    $line .= $chunk;
    if (isset($chunk[3]) && $chunk[3] === ' ') {
      break;
    }
  }
  $code = (int) substr($line, 0, 3);
  return in_array($code, $codes, true);
}

function cd_smtp_send($host, $port, $user, $pass, $to, $fromEmail, $fromName, $replyTo, $subject, $body) {
  $hosts = array_unique(array_filter([$host, 'localhost', '127.0.0.1', 'mail.colddirect.co.uk']));
  foreach ($hosts as $tryHost) {
    $errno = 0;
    $errstr = '';
    $fp = @fsockopen($tryHost, $port ?: 25, $errno, $errstr, 8);
    if (!$fp) {
      error_log('booking.php SMTP connect fail ' . $tryHost . ' ' . $errstr);
      continue;
    }
    stream_set_timeout($fp, 8);
    if (!cd_smtp_expect($fp, [220])) {
      fclose($fp);
      continue;
    }
    fwrite($fp, "EHLO colddirect.co.uk\r\n");
    if (!cd_smtp_expect($fp, [250])) {
      fwrite($fp, "HELO colddirect.co.uk\r\n");
      if (!cd_smtp_expect($fp, [250])) {
        fclose($fp);
        continue;
      }
    }
    if ($user !== '' && $pass !== '') {
      fwrite($fp, "AUTH LOGIN\r\n");
      if (cd_smtp_expect($fp, [334])) {
        fwrite($fp, base64_encode($user) . "\r\n");
        cd_smtp_expect($fp, [334]);
        fwrite($fp, base64_encode($pass) . "\r\n");
        if (!cd_smtp_expect($fp, [235])) {
          error_log('booking.php SMTP auth failed ' . $tryHost);
          fclose($fp);
          continue;
        }
      }
    }
    fwrite($fp, "MAIL FROM:<{$fromEmail}>\r\n");
    if (!cd_smtp_expect($fp, [250])) {
      fclose($fp);
      continue;
    }
    fwrite($fp, "RCPT TO:<{$to}>\r\n");
    if (!cd_smtp_expect($fp, [250, 251])) {
      fclose($fp);
      continue;
    }
    fwrite($fp, "DATA\r\n");
    if (!cd_smtp_expect($fp, [354])) {
      fclose($fp);
      continue;
    }
    $encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
    $headers = "From: {$fromName} <{$fromEmail}>\r\n"
      . "To: <{$to}>\r\n"
      . "Reply-To: {$replyTo}\r\n"
      . "Subject: {$encodedSubject}\r\n"
      . "MIME-Version: 1.0\r\n"
      . "Content-Type: text/plain; charset=UTF-8\r\n"
      . "\r\n"
      . $body
      . "\r\n.\r\n";
    fwrite($fp, $headers);
    $ok = cd_smtp_expect($fp, [250]);
    fwrite($fp, "QUIT\r\n");
    fclose($fp);
    if ($ok) {
      return true;
    }
  }
  return false;
}
