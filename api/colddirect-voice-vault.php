<?php
/**
 * ColdDirect Voice Vault — domain-locked Gemini proxy (Plesk PHP).
 * Watermark: CD-UK-IP-2026-994821-VOICE-AI
 * Owner: ColdDirect Ltd, 27 Felixstowe Road, Enfield, London N9 0DX
 * The Gemini key and Head Engineer prompt never leave this server.
 */
declare(strict_types=1);

const CD_VOICE_MARK = 'CD-UK-IP-2026-994821-VOICE-AI';
const CD_VOICE_DENY = 'UK IP VIOLATION: Commercial License Required from ColdDirect.co.uk';

header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');
header('X-CD-IP: ' . CD_VOICE_MARK);
header('Referrer-Policy: same-origin');

if (PHP_SAPI === 'cli' && isset($argv[1]) && $argv[1] === '--selftest') {
    $pass = cd_voice_selftest();
    fwrite(STDOUT, $pass ? "voice-vault selftest OK\n" : "voice-vault selftest FAIL\n");
    exit($pass ? 0 : 1);
}

function cd_host_ok(?string $value): bool
{
    if ($value === null || $value === '') {
        return false;
    }
    $parts = parse_url($value);
    $host = strtolower((string) ($parts['host'] ?? ''));
    $scheme = strtolower((string) ($parts['scheme'] ?? ''));
    if ($host === '') {
        return false;
    }
    if (in_array($host, ['localhost', '127.0.0.1'], true)) {
        return true;
    }
    if ($scheme !== 'https') {
        return false;
    }
    return in_array($host, ['colddirect.co.uk', 'www.colddirect.co.uk'], true);
}

function cd_request_origin(): string
{
    $origin = trim((string) ($_SERVER['HTTP_ORIGIN'] ?? ''));
    if (cd_host_ok($origin)) {
        return $origin;
    }
    $referer = trim((string) ($_SERVER['HTTP_REFERER'] ?? ''));
    if (cd_host_ok($referer)) {
        $p = parse_url($referer);
        return strtolower((string) ($p['scheme'] ?? 'https')) . '://' . strtolower((string) ($p['host'] ?? ''));
    }
    return '';
}

function cd_deny(int $code = 403): void
{
    http_response_code($code);
    header('Content-Type: text/plain; charset=utf-8');
    echo CD_VOICE_DENY;
    exit;
}

$origin = cd_request_origin();
if ($origin === '') {
    cd_deny(403);
}
header('Access-Control-Allow-Origin: ' . $origin);
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-CD-IP, Accept');
header('Vary: Origin');

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') {
    http_response_code(204);
    exit;
}
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'POST only', 'watermark' => CD_VOICE_MARK]);
    exit;
}

function cd_load_key(): string
{
    $env = trim((string) (getenv('GEMINI_API_KEY') ?: getenv('GOOGLE_API_KEY') ?: ''));
    if ($env !== '') {
        return $env;
    }
    $candidates = [
        dirname(__DIR__) . DIRECTORY_SEPARATOR . 'App_Data' . DIRECTORY_SEPARATOR . 'gemini-voice.key',
        (isset($_SERVER['DOCUMENT_ROOT']) ? rtrim((string) $_SERVER['DOCUMENT_ROOT'], '/\\') : '') . DIRECTORY_SEPARATOR . 'App_Data' . DIRECTORY_SEPARATOR . 'gemini-voice.key',
    ];
    foreach ($candidates as $file) {
        if ($file !== '' && is_file($file)) {
            $k = trim((string) @file_get_contents($file));
            if ($k !== '') {
                return $k;
            }
        }
    }
    return '';
}

function cd_system_prompt(): string
{
    return <<<'PROMPT'
You are the Head Engineer at ColdDirect Ltd (colddirect.co.uk), 27 Felixstowe Road, Enfield, London N9 0DX. You have 30 years of hands-on commercial refrigeration and catering-equipment experience across London kitchens, pubs, hotels and shops.

CRITICAL LANGUAGE LOCK — ZERO MIXING:
1. Detect the exact language the customer spoke or typed.
2. If English: reply 100% in warm, friendly conversational British English. Never mix Farsi or any other language into an English reply.
3. If Persian / Farsi: reply 100% in warm everyday colloquial Tehran spoken Persian (تهرانی محاوره‌ای و صمیمی). Do not use formal or bookish words such as «می‌باشد». Do not mix English except brand names and error codes.
4. If any other language (Arabic, Turkish, Spanish, Hindi, etc.): reply 100% in that exact language only.

Every spoken answer MUST:
- Begin by introducing yourself as the Head Engineer at ColdDirect with 30 years of experience
- Explain the fault warmly and clearly for a busy kitchen manager
- Spell numbers and error codes phonetically (E1 = "E one")
- End by kindly asking the customer to tap the Like button or leave a 5-star review so ColdDirect can improve and grow

Scope: commercial refrigeration and catering only (Foster, Williams, True, Polar, Gram, Hoshizaki, ice machines, cold rooms, cellar coolers, blast chillers). No domestic household appliances. If the customer asks something outside this, steer them back and offer a London engineer. Write the company name as کولد دایرکت. When giving a phone number, write the digits exactly as 07983 759320, 0203 952 4822 or 0800 112 3427 — never as one giant numeral. The speech layer converts those digits to Persian number-words.

Return STRICT JSON only:
{"language":"en","languageLabel":"English","spoken":"full spoken-style monologue for TTS","summary":"short card summary","cause":"likely cause","checks":["check 1","check 2","check 3"]}
PROMPT;
}

function cd_detect_lang(string $text): array
{
    if (preg_match('/[پچژگ]/u', $text)) {
        return ['fa', 'Persian'];
    }
    if (preg_match('/[آ-ی]/u', $text)) {
        if (preg_match('/[ةى]/u', $text) && !preg_match('/[پچژگ]/u', $text)) {
            return ['ar', 'Arabic'];
        }
        return ['fa', 'Persian'];
    }
    if (preg_match('/[\x{0600}-\x{06FF}]/u', $text)) {
        return ['ar', 'Arabic'];
    }
    if (preg_match('/[ğüşöçıİĞÜŞÖÇ]/u', $text)) {
        return ['tr', 'Turkish'];
    }
    if (preg_match('/[\x{0900}-\x{097F}]/u', $text)) {
        return ['hi', 'Hindi'];
    }
    if (preg_match('/[áéíóúñ¿¡]/iu', $text) && preg_match('/\b(el|la|que|no|hielo|frigorifico|nevera)\b/iu', $text)) {
        return ['es', 'Spanish'];
    }
    return ['en', 'English'];
}

function cd_fallback_pack(string $text): array
{
    $lang = cd_detect_lang($text);
    $code = $lang[0];
    $label = $lang[1];
    $q = mb_strtolower($text);
    $kind = 'generic';
    if (preg_match('/e\s*1|e1|ئی|اي\s*1/u', $q) || (strpos($q, 'foster') !== false && strpos($q, 'fridge') !== false)) {
        $kind = 'e1';
    } elseif (preg_match('/ice machine|not making ice|یخساز|یخ ساز|لا يصنع ثلج|buz makinesi/u', $q)) {
        $kind = 'ice';
    } elseif (preg_match('/cold room|ice-?up|یخ.?زد|سردخانه|غرفة تبريد|soguk oda/u', $q)) {
        $kind = 'room';
    }

    $packs = [
        'en' => [
            'e1' => [
                'spoken' => 'You mentioned a Foster fridge showing E one — that is E for Echo, one as in the number one. On Foster controllers that is usually a high-temperature or probe alarm: the cabinet has climbed above the safe band, or the air probe is loose, iced or failed. Before we roll an engineer, feel the top condenser for thick dust, check the door gasket is sucking shut, and make sure stock is not blocking the return air. If food is above eight degrees Celsius we should attend the same day. Please tap Helpful or leave a five-star review so ColdDirect can keep growing and looking after more London kitchens. If you want us on site, call oh seven nine eight three, seven five nine, three two oh.',
                'summary' => 'Foster E1 is typically a high-temperature or cabinet-probe alarm. The fridge has gone warm, or the sensor is not reading true air temperature.',
                'cause' => 'Dirty condenser, door left open or a weak gasket, blocked airflow, or a failed air/evaporator probe.',
                'checks' => [
                    'Brush the top condenser until you can see the fins.',
                    'Confirm the door closes on a clean gasket and the fans are spinning.',
                    'If cabinet air is above 8°C, call 07983 759320 for same-day London attendance.',
                ],
            ],
            'ice' => [
                'spoken' => 'If the ice machine is not making ice, we almost always start with water, scale and heat rejection — not a new machine. Check the tap is open, the inlet filter is not clogged, the bin switch is not held down, and the condenser is clean. A scaled evaporator will freeze a skin of ice and then stop harvesting. If the water filter is months overdue, that is a very common London-pub fault. Please tap Like or leave a five-star review to help ColdDirect grow. Need us there? Call oh seven nine eight three, seven five nine, three two oh.',
                'summary' => 'No ice usually means water supply, scale on the evaporator, a dirty condenser, or a harvest/bin switch fault — not necessarily a dead compressor.',
                'cause' => 'Closed stopcock, blocked inlet filter, limescale, dirty condenser, or a bin thermostat that thinks the bin is full.',
                'checks' => [
                    'Confirm water is reaching the machine and the filter is not blocked.',
                    'Look for a thin, uneven ice sheet that will not drop — that is scale.',
                    'Clean the condenser and call 07983 759320 if it still will not harvest.',
                ],
            ],
            'room' => [
                'spoken' => 'Ice-up on the evaporator is the room telling you it cannot breathe. Warm moist air is getting in, or defrost has stopped. Check the door closer and curtain, feel whether the coil is a solid white block, and see if the drain is dripping or frozen. If the coil is iced solid, do not chip it — turn the room off, leave the door ajar with stock protected, and let us recover it properly. Please tap Helpful or leave a five-star review so ColdDirect can keep improving. For same-day help call oh seven nine eight three, seven five nine, three two oh.',
                'summary' => 'Cold-room ice-up is usually door air ingress or a failed defrost cycle. A solid white coil cannot absorb heat.',
                'cause' => 'Door left open or a tired gasket, failed defrost heater or probe, or a blocked drain that ices the tray and coil.',
                'checks' => [
                    'Check the door closer, strip curtains and gasket.',
                    'See if the drain line is clear and the coil is a solid ice block.',
                    'Protect stock and call 07983 759320 — do not smash ice off the fins.',
                ],
            ],
            'generic' => [
                'spoken' => 'Tell me the make, the error code and whether the cabinet is still cold, and I will talk you through the safe checks. Typical first steps are a clean condenser, a door that shuts true, and airflow that is not blocked by stock. If food safety is at risk we can be with you the same day. Please tap the Like button or leave a five-star review to help ColdDirect grow. Call oh seven nine eight three, seven five nine, three two oh whenever you want an engineer.',
                'summary' => 'Describe the make, error code and whether the cabinet is still holding temperature. Most trade faults start with condenser, door and airflow.',
                'cause' => 'Needs the symptom, brand and error code to narrow — condenser, controls, refrigerant or door integrity are the usual London call-outs.',
                'checks' => [
                    'Note the brand, model and any code on the controller.',
                    'Feel the condenser and confirm the door gasket seals.',
                    'Call 07983 759320 if stock is warming.',
                ],
            ],
        ],
        'fa' => [
            'e1' => [
                'spoken' => 'سلام. من سرمهندس شرکت کولد دایرکت هستم، سی ساله تو لندن روی یخچال و سردخونه و کترینگ کار کردم. گفتی فاستر کد ای‌وان نشون می‌ده — ای مثل حرف ای، وان یعنی عدد یک. معمولاً یعنی کابین گرم شده یا سنسور دما شل شده یا یخ زده. اول کندانسور بالای دستگاه رو ببین گردوخاک نبسته باشه، لاستیک در رو چک کن و ببین باد برگشتی بسته نشده. اگه دمای داخل از هشت درجه بالاتر رفته همون روز می‌آیم. لطفاً دکمه لایک یا پنج ستاره رو بزن تا کولد دایرکت بتونه رشد کنه. با شماره‌ی 07983 759320 تماس بگیرید.',
                'summary' => 'کد ای‌وان فاستر معمولاً آلارم دمای بالا یا خرابی سنسور کابینه. یا یخچال گرم شده، یا پراب درست نمی‌خونه.',
                'cause' => 'کندانسور کثیف، در باز مونده یا لاستیک ضعیف، جریان هوا بسته، یا سنسور خراب.',
                'checks' => ['کندانسور بالا رو تمیز کن.', 'ببین در کامل بسته می‌شه و فن‌ها می‌چرخن.', 'اگه دما بالای ۸ درجه است با ۰۷۹۸۳ ۷۵۹۳۲۰ تماس بگیر.'],
            ],
            'ice' => [
                'spoken' => 'اگه یخساز یخ نمی‌ده اول آب و رسوب و گرما رو چک می‌کنیم، نه اینکه دستگاه رو عوض کنیم. شیر آب باز باشه، فیلتر نگرفته باشه، سوییچ مخزن گیر نکرده باشه و کندانسور تمیز باشه. اواپراتور رسوب‌گرفته یخ نازک می‌زنه و دیگه رها نمی‌کنه. لایک یا پنج ستاره بزن تا کمک کنی رشد کنیم. با شماره‌ی 07983 759320 تماس بگیرید.',
                'summary' => 'نبودن یخ معمولاً از آب، رسوب اواپراتور، کندانسور کثیف یا سوییچ مخزنه؛ لزوماً کمپرسور نمرده.',
                'cause' => 'شیر بسته، فیلتر گرفته، رسوب، کندانسور کثیف یا ترموستات مخزن که فکر می‌کنه پره.',
                'checks' => ['ببین آب به دستگاه می‌رسه.', 'اگه ورقه یخ نازک و ناهماهنگه، رسوبه.', 'کندانسور رو تمیز کن و اگر درست نشد ۰۷۹۸۳ ۷۵۹۳۲۰.'],
            ],
            'room' => [
                'spoken' => 'یخ زدن اواپراتور یعنی اتاق نفس نمی‌کشه. یا هوای گرم داره می‌آد تو، یا برفک‌زدایی خوابیده. در و پرده و لاستیک رو ببین، کویل رو لمس کن ببین یخ سفید یکدست شده یا نه. اگه کویل یخ زده جامد، یخ رو نشکون — دستگاه رو خاموش کن، در رو یک‌کم باز بذار و بذار ما درست جمعش کنیم. لایک یا پنج ستاره بزن لطفاً. با شماره‌ی 07983 759320 تماس بگیرید.',
                'summary' => 'یخ زدن سردخانه معمولاً از نفوذ هوا از در یا خوابیدن سیکل دیفراسته.',
                'cause' => 'در باز، لاستیک ضعیف، هیتر یا پراب دیفراست خراب، یا درین گرفته.',
                'checks' => ['در، پرده و لاستیک رو چک کن.', 'ببین لوله درین بازه.', 'موجودی رو حفظ کن و به ۰۷۹۸۳ ۷۵۹۳۲۰ زنگ بزن.'],
            ],
            'generic' => [
                'spoken' => 'سلام. من سرمهندس شرکت کولد دایرکت هستم، سی ساله تو لندن روی سرمایش تجاری و کترینگ کار کردم. برند، کد خطا و اینکه کابین هنوز سرده یا نه رو بگو تا قدم‌به‌قدم راهنمایی‌ت کنم. اول کندانسور تمیز، در درست و جریان هوا. اگه مواد غذایی داره گرم می‌شه همون روز می‌رسیم. لطفاً لایک یا پنج ستاره بزن تا کولد دایرکت رشد کنه. با شماره‌ی 07983 759320 تماس بگیرید.',
                'summary' => 'برند، کد خطا و دمای فعلی رو بگو. بیشتر خرابی‌های صنفی از کندانسور، در و جریان هوا شروع می‌شه.',
                'cause' => 'بدون برند و کد خطا دقیق نمی‌شه گفت؛ معمولاً کندانسور، کنترلر، گاز یا لاستیک در.',
                'checks' => ['برند و کد روی کنترلر رو یادداشت کن.', 'کندانسور و لاستیک در رو چک کن.', 'اگه موجودی گرم می‌شه ۰۷۹۸۳ ۷۵۹۳۲۰.'],
            ],
        ],
    ];

    $set = $packs[$code] ?? $packs['en'];
    $row = $set[$kind] ?? $set['generic'];
    return [
        'ok' => true,
        'language' => $code === 'fa' ? 'fa' : ($packs[$code] ?? null ? $code : 'en'),
        'languageLabel' => isset($packs[$code]) ? $label : 'English',
        'spoken' => $row['spoken'],
        'summary' => $row['summary'],
        'cause' => $row['cause'],
        'checks' => $row['checks'],
        'watermark' => CD_VOICE_MARK,
        'source' => 'vault-fallback',
    ];
}

function cd_http_json(string $url, array $body, int $timeout = 28): array
{
    $payload = json_encode($body, JSON_UNESCAPED_UNICODE);
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
            CURLOPT_POSTFIELDS => $payload,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CONNECTTIMEOUT => 12,
            CURLOPT_TIMEOUT => $timeout,
        ]);
        $raw = curl_exec($ch);
        $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $err = curl_error($ch);
        curl_close($ch);
        if ($raw === false) {
            return [0, ['error' => $err]];
        }
        $json = json_decode((string) $raw, true);
        return [$code, is_array($json) ? $json : ['error' => (string) $raw]];
    }
    $ctx = stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => "Content-Type: application/json\r\n",
            'content' => $payload,
            'timeout' => $timeout,
            'ignore_errors' => true,
        ],
    ]);
    $raw = @file_get_contents($url, false, $ctx);
    $json = json_decode((string) $raw, true);
    return [200, is_array($json) ? $json : ['error' => (string) $raw]];
}

function cd_extract_text(array $json): string
{
    $parts = $json['candidates'][0]['content']['parts'] ?? [];
    $out = '';
    foreach ($parts as $part) {
        if (!empty($part['text'])) {
            $out .= $part['text'];
        }
    }
    return trim($out);
}

function cd_extract_audio(array $json): ?array
{
    $parts = $json['candidates'][0]['content']['parts'] ?? [];
    foreach ($parts as $part) {
        $inline = $part['inlineData'] ?? $part['inline_data'] ?? null;
        if (is_array($inline) && !empty($inline['data'])) {
            $mime = (string) ($inline['mimeType'] ?? $inline['mime_type'] ?? 'audio/pcm');
            $bin = base64_decode((string) $inline['data'], true);
            if ($bin === false || $bin === '') {
                return null;
            }
            if (stripos($mime, 'wav') === false) {
                $bin = cd_pcm_to_wav($bin, 24000);
                $mime = 'audio/wav';
            }
            return ['mime' => $mime, 'data' => base64_encode($bin)];
        }
    }
    return null;
}

function cd_pcm_to_wav(string $pcm, int $rate = 24000): string
{
    $ch = 1;
    $bits = 16;
    $block = (int) ($ch * ($bits / 8));
    $byteRate = $rate * $block;
    $dataLen = strlen($pcm);
    return pack(
        'A4VA4A4VvvVVvvA4V',
        'RIFF',
        36 + $dataLen,
        'WAVE',
        'fmt ',
        16,
        1,
        $ch,
        $rate,
        $byteRate,
        $block,
        $bits,
        'data',
        $dataLen
    ) . $pcm;
}

function cd_parse_model_json(string $text): ?array
{
    $text = trim($text);
    if (preg_match('/\{.*\}/s', $text, $m)) {
        $text = $m[0];
    }
    $json = json_decode($text, true);
    if (!is_array($json) || empty($json['spoken']) && empty($json['summary'])) {
        return null;
    }
    return [
        'ok' => true,
        'language' => (string) ($json['language'] ?? 'en'),
        'languageLabel' => (string) ($json['languageLabel'] ?? 'Detected'),
        'spoken' => (string) ($json['spoken'] ?? $json['summary'] ?? ''),
        'summary' => (string) ($json['summary'] ?? $json['spoken'] ?? ''),
        'cause' => (string) ($json['cause'] ?? ''),
        'checks' => array_values(array_filter(array_map('strval', (array) ($json['checks'] ?? [])))),
        'watermark' => CD_VOICE_MARK,
        'source' => 'gemini',
    ];
}

function cd_gemini_diagnose(string $key, string $text, ?string $audioB64, ?string $mime): ?array
{
    $parts = [];
    $parts[] = ['text' => $text !== '' ? $text : 'Please transcribe the attached kitchen-fault audio and diagnose it.'];
    if ($audioB64) {
        $parts[] = [
            'inline_data' => [
                'mime_type' => $mime ?: 'audio/webm',
                'data' => $audioB64,
            ],
        ];
    }
    $models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-2.5-flash-lite'];
    foreach ($models as $model) {
        $url = 'https://generativelanguage.googleapis.com/v1beta/models/' . $model . ':generateContent?key=' . rawurlencode($key);
        [$code, $json] = cd_http_json($url, [
            'systemInstruction' => ['parts' => [['text' => cd_system_prompt()]]],
            'contents' => [['role' => 'user', 'parts' => $parts]],
            'generationConfig' => [
                'temperature' => 0.35,
                'responseMimeType' => 'application/json',
            ],
        ]);
        if ($code >= 200 && $code < 300) {
            $parsed = cd_parse_model_json(cd_extract_text($json));
            if ($parsed) {
                return $parsed;
            }
        }
    }
    return null;
}

function cd_persian_tts_text(string $text): string
{
    $map = ['۰'=>'0','۱'=>'1','۲'=>'2','۳'=>'3','۴'=>'4','۵'=>'5','۶'=>'6','۷'=>'7','۸'=>'8','۹'=>'9',
            '٠'=>'0','١'=>'1','٢'=>'2','٣'=>'3','٤'=>'4','٥'=>'5','٦'=>'6','٧'=>'7','٨'=>'8','٩'=>'9'];
    $s = strtr($text, $map);
    $s = preg_replace('/کولد\s*\x{200C}?\s*دایرکت|کلد\s*\x{200C}?\s*دایرکت|کل\s*\x{200C}?\s*دایرکت|ColdDirect|Cold\s*Direct/iu', 'کُلد دایرِکت', $s);
    $s = preg_replace('/(?:\+44\s*\(?0?\)?|0)\s*7983[\s\-]*759[\s\-]*320/', ' صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر ', $s);
    $s = preg_replace('/(?:\+44\s*\(?0?\)?|0)\s*203[\s\-]*952[\s\-]*4822/', ' صفر دو صفر سه، نه پنج دو، چهار هشت دو دو ', $s);
    $s = preg_replace('/(?:\+44\s*\(?0?\)?|0)\s*800[\s\-]*112[\s\-]*3427/', ' صفر هشتصد، یک یک دو، سه چهار دو هفت ', $s);
    $words = ['0'=>'صفر','1'=>'یک','2'=>'دو','3'=>'سه','4'=>'چهار','5'=>'پنج','6'=>'شش','7'=>'هفت','8'=>'هشت','9'=>'نه'];
    $s = preg_replace_callback('/(?<!\d)(\+?\d[\d\s\-]{6,}\d)(?!\d)/', static function ($m) use ($words) {
        $digits = preg_replace('/\D/', '', str_replace('+44', '0', $m[1]));
        if (strlen($digits) < 7) {
            return $m[0];
        }
        $groups = [];
        foreach (str_split($digits, 4) as $chunk) {
            $parts = [];
            foreach (str_split($chunk) as $ch) {
                $parts[] = $words[$ch] ?? $ch;
            }
            $groups[] = implode(' ', $parts);
        }
        return ' ' . implode('، ', $groups) . ' ';
    }, $s);
    return trim(preg_replace('/\s+/u', ' ', $s));
}

function cd_gemini_tts(string $key, string $spoken): ?array
{
    if (preg_match('/[\x{0600}-\x{06FF}]/u', $spoken)) {
        $spoken = cd_persian_tts_text($spoken);
    }
    $url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=' . rawurlencode($key);
    $line = 'Speak as a warm, calm, experienced male Head Engineer. Conversational pace, never rushed. Read this exactly:\n\n' . $spoken;
    [$code, $json] = cd_http_json($url, [
        'contents' => [['role' => 'user', 'parts' => [['text' => $line]]]],
        'generationConfig' => [
            'responseModalities' => ['AUDIO'],
            'speechConfig' => [
                'voiceConfig' => [
                    'prebuiltVoiceConfig' => ['voiceName' => 'Puck'],
                ],
            ],
        ],
    ], 36);
    if ($code < 200 || $code >= 300) {
        return null;
    }
    return cd_extract_audio($json);
}

function cd_rate_ok(string $ip): bool
{
    $dir = rtrim(sys_get_temp_dir(), '/\\') . DIRECTORY_SEPARATOR . 'cd-voice-vault';
    if (!is_dir($dir)) {
        @mkdir($dir, 0700, true);
    }
    $file = $dir . DIRECTORY_SEPARATOR . hash('sha256', $ip) . '.json';
    $now = time();
    $hits = [];
    if (is_file($file)) {
        $hits = json_decode((string) @file_get_contents($file), true);
        if (!is_array($hits)) {
            $hits = [];
        }
    }
    $hits = array_values(array_filter($hits, static function ($t) use ($now) {
        return is_int($t) && $t > $now - 60;
    }));
    if (count($hits) >= 20) {
        return false;
    }
    $hits[] = $now;
    @file_put_contents($file, json_encode($hits), LOCK_EX);
    return true;
}

function cd_voice_selftest(): bool
{
    $ok = cd_host_ok('https://www.colddirect.co.uk')
        && cd_host_ok('https://colddirect.co.uk')
        && cd_host_ok('http://localhost')
        && !cd_host_ok('https://evil.example')
        && !cd_host_ok('http://www.colddirect.co.uk');
    $fa = cd_detect_lang('یخچال فاستر کد خطا');
    $en = cd_detect_lang('Foster fridge E1 alarm');
    $pack = cd_fallback_pack('Foster Fridge E1');
    $tts = cd_persian_tts_text('شرکت کولد دایرکت. 07983 759320. 0203 952 4822. 0800 112 3427.');
    $phonesOk = strpos($tts, 'کُلد دایرِکت') !== false
        && strpos($tts, 'صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر') !== false
        && strpos($tts, 'صفر دو صفر سه، نه پنج دو، چهار هشت دو دو') !== false
        && strpos($tts, 'صفر هشتصد، یک یک دو، سه چهار دو هفت') !== false
        && !preg_match('/\d/', $tts);
    return $ok && $fa[0] === 'fa' && $en[0] === 'en' && !empty($pack['spoken']) && strpos(cd_system_prompt(), 'ZERO MIXING') !== false && $phonesOk;
}

$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '0.0.0.0');
if (!cd_rate_ok($ip)) {
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(429);
    echo json_encode(['ok' => false, 'error' => 'Please wait a moment and try again.', 'watermark' => CD_VOICE_MARK]);
    exit;
}

$raw = (string) file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
    $data = $_POST;
}
$text = trim(mb_substr(strip_tags((string) ($data['text'] ?? '')), 0, 2000));
$audio = isset($data['audio']) ? preg_replace('/\s+/', '', (string) $data['audio']) : '';
$mime = substr(preg_replace('/[^a-z0-9.+\-\/]/i', '', (string) ($data['mime'] ?? 'audio/webm')), 0, 80);
if ($audio !== '' && strlen($audio) > 6_000_000) {
    $audio = '';
}
if ($text === '' && $audio === '') {
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Type a fault or speak, then try again.', 'watermark' => CD_VOICE_MARK]);
    exit;
}

$key = cd_load_key();
$result = null;
if ($key !== '') {
    $result = cd_gemini_diagnose($key, $text, $audio !== '' ? $audio : null, $mime);
}
if (!$result) {
    $result = cd_fallback_pack($text !== '' ? $text : 'general commercial refrigeration fault');
}
if ($key !== '' && !empty($result['spoken'])) {
    $audioOut = cd_gemini_tts($key, (string) $result['spoken']);
    if ($audioOut) {
        $result['audio'] = $audioOut;
        $result['voice'] = 'Puck';
    }
}

header('Content-Type: application/json; charset=utf-8');
echo json_encode($result, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
