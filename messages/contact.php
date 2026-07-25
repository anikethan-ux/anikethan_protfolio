<?php
/**
 * contact.php — receives the portfolio contact form submission and
 * appends it as plain text to messages/messages.txt.
 *
 * IMPORTANT: This only works on a server that runs PHP.
 * GitHub Pages serves static files only — it CANNOT execute this file.
 * Use this on PHP-capable hosting (shared hosting, XAMPP/local PHP server,
 * etc.). See README.md for details and alternatives.
 */

header('Content-Type: application/json');

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Collect + sanitize input
$name    = trim($_POST['name'] ?? '');
$email   = trim($_POST['email'] ?? '');
$message = trim($_POST['message'] ?? '');

// Basic validation
if ($name === '' || $email === '' || $message === '') {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'All fields are required.']);
    exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid email address.']);
    exit;
}

// Strip anything that could break the text file's structure
$clean = function ($str) {
    return str_replace(["\r\n", "\r", "\n"], ' ', $str);
};

// Make sure the messages/ folder exists
$folder = __DIR__ . '/messages';
if (!is_dir($folder)) {
    mkdir($folder, 0755, true);
}

$file = $folder . '/messages.txt';

$entry = sprintf(
    "[%s] Name: %s | Email: %s | Message: %s%s",
    date('Y-m-d H:i:s'),
    $clean($name),
    $clean($email),
    $clean($message),
    PHP_EOL
);

// Append the message (creates the file if it doesn't exist yet)
$result = file_put_contents($file, $entry, FILE_APPEND | LOCK_EX);

if ($result === false) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Could not save message.']);
    exit;
}

echo json_encode(['success' => true]);
