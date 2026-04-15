<?php

declare(strict_types=1);

require_once __DIR__ . "/lib.php";

[$yocalPath, $masterPath] = db_paths();
$db = connect_sqlite($yocalPath);
$masterDb = connect_sqlite($masterPath);

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if (($_SERVER["REQUEST_METHOD"] ?? "GET") === "OPTIONS") {
    http_response_code(204);
    exit;
}

function json_response(array $payload, int $status = 200): void
{
    http_response_code($status);
    header("Content-Type: application/json; charset=utf-8");
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}

$path = parse_url($_SERVER["REQUEST_URI"] ?? "/", PHP_URL_PATH) ?: "/";

$baseFolder = '/api-php';  // the name of the parent folder
if (str_starts_with($path, $baseFolder)) {
    $path = substr($path, strlen($baseFolder));
}

if ($path === "/test") {
    header("Content-Type: text/html; charset=utf-8");
    echo "<p>Hello, World!</p>";
    exit;
}

if ($path === "/") {
    $data = get_date_data($db, $masterDb, new DateTimeImmutable("today"));
    json_response($data);
    exit;
}

if ($path === "/date") {
    $date = parse_query_date($_GET);
    if ($date === null) {
        json_response(["error" => "year, month, and day are required"], 400);
        exit;
    }
    json_response(get_date_data($db, $masterDb, $date));
    exit;
}

if ($path === "/test-display") {
    $date = parse_query_date($_GET) ?? new DateTimeImmutable("today");
    $data = get_date_data($db, $masterDb, $date);

    if (array_keys($data) === ["error"]) {
        json_response($data, 404);
        exit;
    }

    header("Content-Type: text/html; charset=utf-8");
    require __DIR__ . "/template.php";
    exit;
}

json_response(["error" => "Not found"], 404);
