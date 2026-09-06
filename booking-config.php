<?php
/**
 * Booking mail + optional mobile webhook.
 * Email goes to Hotmail so Outlook on your phone can push instantly
 * if notifications are on for coldcom@hotmail.co.uk.
 *
 * Optional webhook (free): create a topic at https://ntfy.sh then paste:
 *   'webhook_url' => 'https://ntfy.sh/your-private-topic-name',
 * Install the ntfy app, subscribe to that topic.
 *
 * Optional Resend (free tier): paste API key from https://resend.com
 */
return [
  'to_email' => 'coldcom@hotmail.co.uk',
  'from_email' => 'noreply@colddirect.co.uk',
  'from_name' => 'Cold Direct Website',
  'resend_api_key' => '',
  'webhook_url' => '',
];
