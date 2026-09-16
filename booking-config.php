<?php
/**
 * Booking mail + optional mobile webhook.
 * Email goes to info@colddirect.co.uk so notifications can push on phone.
 *
 * Optional webhook (free): create a topic at https://ntfy.sh then paste:
 *   'webhook_url' => 'https://ntfy.sh/your-private-topic-name',
 * Install the ntfy app, subscribe to that topic.
 *
 * Optional Resend (free tier): paste API key from https://resend.com
 */
return [
  'to_email' => 'info@colddirect.co.uk',
  'from_email' => 'info@colddirect.co.uk',
  'from_name' => 'Cold Direct Website',
  'smtp_host' => 'localhost',
  'smtp_port' => 25,
  'smtp_user' => '',
  'smtp_pass' => '',
  'resend_api_key' => '',
  'webhook_url' => 'https://ntfy.sh/cold-direct-bookings-221345',
];
