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
You are a commercial refrigeration diagnostic engine for Cold Direct Ltd, London. Kind, polite, no slang.
NEVER introduce yourself. NEVER write a greeting. NEVER include phone numbers, Like, review, or closing text.
Output ONLY 2 short sentences diagnosing the fault in the user's language. If they ask to translate, output in that requested language. If audio is Persian, write Persian.
Return STRICT JSON only: {"target_language_code":"BCP-47 e.g. fa-IR","transcript":"exact customer words in native script","technical_answer":"exactly two short diagnostic sentences, no greeting, no phones, no like/review"}
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
                'spoken' => 'درود، من سرپرست مهندسین در شرکت کولد دایرکت هستم و خوشحالم که ما را انتخاب کردید. گفتی فاستر کد ای‌وان نشون می‌ده — ای مثل حرف ای، وان یعنی عدد یک. معمولاً یعنی کابین گرم شده یا سنسور دما شل شده یا یخ زده. اول کندانسور بالای دستگاه رو ببین گردوخاک نبسته باشه، لاستیک در رو چک کن و ببین باد برگشتی بسته نشده. اگه دمای داخل از هشت درجه بالاتر رفته همون روز می‌آیم. اگر این راهنمایی برای شما مفید بود، لطفاً دکمه سبز لایک و ثبت نظر پنج‌ستاره را در پایین همین کادر بزنید. با شماره‌ی 07983 759320 تماس بگیرید.',
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
                'spoken' => 'درود، من سرپرست مهندسین در شرکت کولد دایرکت هستم و خوشحالم که ما را انتخاب کردید. برند، کد خطا و اینکه کابین هنوز سرده یا نه رو بگو تا قدم‌به‌قدم راهنمایی‌ت کنم. اول کندانسور تمیز، در درست و جریان هوا. اگه مواد غذایی داره گرم می‌شه همون روز می‌رسیم. اگر این راهنمایی برای شما مفید بود، لطفاً دکمه سبز لایک و ثبت نظر پنج‌ستاره را در پایین همین کادر بزنید. با شماره‌ی 07983 759320 تماس بگیرید.',
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
    if (!is_array($json)) {
        return null;
    }
    $display = (string) ($json['technical_answer'] ?? $json['display_text'] ?? $json['spoken'] ?? $json['summary'] ?? '');
    $spokenTts = (string) ($json['spoken_text'] ?? $json['tts_text'] ?? '');
    if (!is_array($json) || ($display === '' && $spokenTts === '')) {
        return null;
    }
    if ($display === '') {
        $display = $spokenTts;
    }
    $code = strtolower((string) ($json['target_language_code'] ?? $json['language'] ?? 'en'));
    if (strpos($code, 'fil') === 0 || strpos($code, 'tl') === 0) {
        $code = 'tl';
    } elseif (strlen($code) > 2) {
        $code = substr($code, 0, 2);
    }
    if ($spokenTts === '') {
        $spokenTts = $display;
    }
    if (!preg_match('/759320|952\s*4822|0203|07983/u', $display) || !preg_match('/like|review|لایک|ستاره|beğeni|bituin|estrellas|نجمة/iu', $display)) {
        $display .= ' 0203 952 4822 / 07983 759320. Like & 5-Star Review.';
    }
    return [
        'ok' => true,
        'language' => $code,
        'languageLabel' => (string) ($json['languageLabel'] ?? 'Detected'),
        'spoken' => $display,
        'display_text' => $display,
        'tts_text' => $spokenTts,
        'spoken_text' => $spokenTts,
        'summary' => (string) ($json['summary'] ?? $display),
        'cause' => (string) ($json['cause'] ?? $json['likely_cause'] ?? ''),
        'checks' => array_values(array_filter(array_map('strval', (array) ($json['checks'] ?? $json['quick_checks'] ?? [])))),
        'watermark' => CD_VOICE_MARK,
        'source' => 'llm',
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

function cd_strip_persian_frame(string $text): string
{
    $s = $text;
    $s = preg_replace('/^دُرود بر شُما[\s\S]*?اِنتِخاب کَردید\.?\s*/u', '', $s);
    $s = preg_replace('/^درود بر شما[\s\S]*?انتخاب کردید\.?\s*/u', '', $s);
    $s = preg_replace('/^درود[^.!?؟]*[.!?؟]?\s*/u', '', $s);
    $s = preg_replace('/^سلام[^.!?؟]*[.!?؟]?\s*/u', '', $s);
    $s = preg_replace('/\s*برای اعزام فوری[\s\S]*$/u', '', $s);
    $s = preg_replace('/\s*چِنانچه مُشکِل[\s\S]*$/u', '', $s);
    $s = preg_replace('/\s*اگر این راهنمایی[\s\S]*$/u', '', $s);
    $s = preg_replace('/\s*اَگَر این راهْنَمایی[\s\S]*$/u', '', $s);
    $s = preg_replace('/(?:\+44\s*\(?0?\)?|0)\s*7983[\s\-]*759[\s\-]*320/', ' ', $s);
    $s = preg_replace('/(?:\+44\s*\(?0?\)?|0)\s*203[\s\-]*952[\s\-]*4822/', ' ', $s);
    $s = preg_replace('/(?:\+44\s*\(?0?\)?|0)\s*800[\s\-]*112[\s\-]*3427/', ' ', $s);
    $s = trim(preg_replace('/\s+/u', ' ', $s));
    $parts = preg_split('/(?<=[.!?؟])\s+/u', $s);
    if (is_array($parts) && count($parts) > 2) {
        $s = trim($parts[0] . ' ' . $parts[1]);
    }
    return $s;
}

function cd_persian_tts_text(string $text): string
{
    $s = cd_strip_persian_frame($text);
    $s = str_replace('سردخانه', 'سَردخانه', $s);
    $s = str_replace('یخچال', 'یَخچالِ', $s);
    $s = str_replace('کمپرسور', 'کُمپرِسور', $s);
    $s = str_replace('ترموستات', 'تِرموستات', $s);
    $s = str_replace('کندانسور', 'کُندانسور', $s);
    $s = str_replace('اواپراتور', 'اِواپُراتور', $s);
    $s = preg_replace('/کولد\s*دایرکت|ColdDirect|Cold Direct/iu', 'کُلد دایرِکت', $s);
    return 'درود بر شما. من مهندس ارشد شرکت کُلد دایرِکت هستم و خوشحالم که ما را انتخاب کردید. '
        . trim($s) . ' '
        . 'برای اعزام فوری تکنسین در لندن، با شماره تلفن صفر دویست و سه، نهصد و پنجاه و دو، چهل و هشت، بیست و دو، و یا موبایل صفر هفتصد و نود و هشت، سی و هفت، پنجاه و نه، سیصد و بیست تماس بگیرید. اگر این راهنمایی برای شما مفید بود، ممنون می‌شویم دکمه سبز لایک و ثبت نظر پنج ستاره را در پایین همین کادر بزنید.';
}

function cd_gemini_tts(string $key, string $spoken): ?array
{
    if (preg_match('/[\x{0600}-\x{06FF}]/u', $spoken)) {
        return null;
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
    $tts = cd_persian_tts_text('کندانسور کثیف است. لاستیک در را چک کنید. 07983 759320');
    $phonesOk = strpos($tts, 'درود بر شما') !== false
        && strpos($tts, 'صفر دویست و سه') !== false
        && strpos($tts, 'صفر هفتصد و نود و هشت') !== false
        && strpos($tts, 'کُندانسور') !== false
        && strpos($tts, '07983') === false;
    return $ok && $fa[0] === 'fa' && $en[0] === 'en' && !empty($pack['spoken']) && strpos(cd_system_prompt(), 'target_language_code') !== false && $phonesOk;
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
