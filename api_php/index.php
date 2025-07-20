<?php

ini_set('display_errors', 1);

require_once 'functions.php';

// Set the content type to JSON
header('Content-Type: application/json');

// Handle the routes
$base_path = dirname($_SERVER['SCRIPT_NAME']);
$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);
$path = '/' . ltrim(str_replace($base_path, '', $path), '/');

if ($path === '/' || $path === '/index.php') {
    echo json_encode(get_today());
} elseif ($path === '/date') {
    if (isset($_GET['year']) && isset($_GET['month']) && isset($_GET['day'])) {
        $year = (int)$_GET['year'];
        $month = (int)$_GET['month'];
        $day = (int)$_GET['day'];
        echo json_encode(get_date_from_request($year, $month, $day));
    } else {
        http_response_code(400);
        echo json_encode(['error' => 'Year, month, and day parameters are required.']);
    }
} elseif ($path === '/test-display') {
    $year = isset($_GET['year']) ? (int)$_GET['year'] : (int)date('Y');
    $month = isset($_GET['month']) ? (int)$_GET['month'] : (int)date('m');
    $day = isset($_GET['day']) ? (int)$_GET['day'] : (int)date('d');

    $data = get_date_from_request($year, $month, $day);

    if (isset($data['error'])) {
        http_response_code(404);
        echo json_encode($data);
    } else {
        echo render_template(__DIR__ . 'test_display.html.twig', ['data' => $data]);
    }
} else {
    http_response_code(404);
    echo json_encode(['error' => "Not Found ($path)"]);
}
