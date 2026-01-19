<?php

// Enable assertions
ini_set('assert.active', 1);
ini_set('assert.warning', 1);
ini_set('assert.bail', 0); // Don't bail on failure, to allow reporting

// Mock WordPress functions to allow the script to run standalone
if (!function_exists('get_header')) {
    function get_header() {
        echo "<!-- Mock Header -->\n";
    }
}

if (!function_exists('get_footer')) {
    function get_footer() {
        echo "<!-- Mock Footer -->\n";
    }
}

if (!function_exists('add_action')) {
    function add_action($hook, $function_name) {
        // Do nothing
    }
}

if (!function_exists('wp_enqueue_script')) {
    function wp_enqueue_script($handle) {
        // Do nothing
    }
}

if (!function_exists('wp_register_style')) {
    function wp_register_style($handle, $src) {
        // Do nothing
    }
}

if (!function_exists('wp_enqueue_style')) {
    function wp_enqueue_style($handle) {
        // Do nothing
    }
}

if (!function_exists('wp_upload_dir')) {
    function wp_upload_dir() {
        return ['basedir' => __DIR__ . '/../db'];
    }
}

echo "--- Running Test for daily_template.php ---\n\n";

// --- Test Case 1: Daily with Specific Date ---
echo "--- Testing with date 2025-07-20 ---\n";
// Simulate a form submission by setting the $_POST variable
$_POST['mydate'] = '2025-07-20';

// Capture the output of the included file
ob_start();
include 'daily_template.php';
$output = ob_get_clean();

// Define expected content
$expected_strings = [
    'Sunday 20th',
    'Holy Prophet Elijah (Elias)',
    'Romans 12:6-14',
    'Matthew 9:1-8',
    'James 5:10-20'
];

$all_found = true;
foreach ($expected_strings as $expected) {
    if (strpos($output, $expected) === false) {
        $all_found = false;
        $error_file = __DIR__ . '/test_output_failed.html';
        file_put_contents($error_file, $output);
        echo "Assertion Failed: Did not find expected string '{$expected}' in the output.\n";
        echo "The full output has been saved to: {$error_file}\n";
        break; // Stop on first failure
    }
}

if ($all_found) {
    echo "Test Case 1 PASSED: All expected content was found.\n";
} else {
    echo "Test Case 1 FAILED.\n";
}

echo "\n";


// --- Test Case 2: Daily for Today's Date (empty post) ---
echo "--- Testing with today's date (empty \$_POST) ---\n";
// Unset the post variable to simulate the initial page load
unset($_POST['mydate']);

// Capture output to prevent it from cluttering the test results
ob_start();
include 'daily_template.php';
$output = ob_get_clean();

// Define expected content
$expected_strings = [
    'h2 class="lectionary-single-header"',
    'p class="lectionary-single-saints"',
    '<em>Today&#39;s Readings:</em>',
];

$all_found = true;
foreach ($expected_strings as $expected) {
    if (strpos($output, $expected) === false) {
        $all_found = false;
        $error_file = __DIR__ . '/test_output_failed.html';
        file_put_contents($error_file, $output);
        echo "Assertion Failed: Did not find expected string '{$expected}' in the output.\n";
        echo "The full output has been saved to: {$error_file}\n";
        break; // Stop on first failure
    }
}

if ($all_found) {
    echo "Test Case 2 PASSED: All expected content was found.\n";
} else {
    echo "Test Case 2 FAILED.\n";
}


// --- Test Case 3: This month ---
echo "--- Testing this month ---\n";
// Unset the post variable to simulate the initial page load

// Capture output to prevent it from cluttering the test results
ob_start();
include 'this_month_template.php';
$output = ob_get_clean();

// Define expected content
$expected_strings = [
    '<h2>This Month\'s Saints and Readings</h2>',
    '<em>Commemorations:</em>',
];

$all_found = true;
foreach ($expected_strings as $expected) {
    if (strpos($output, $expected) === false) {
        $all_found = false;
        $error_file = __DIR__ . '/test_output_failed.html';
        file_put_contents($error_file, $output);
        echo "Assertion Failed: Did not find expected string '{$expected}' in the output.\n";
        echo "The full output has been saved to: {$error_file}\n";
        break; // Stop on first failure
    }
}

if ($all_found) {
    echo "Test Case 3 PASSED: All expected content was found.\n";
} else {
    echo "Test Case 3 FAILED.\n";
}


// --- Test Case 4: Next month ---
echo "--- Testing next month ---\n";
// Unset the post variable to simulate the initial page load

// Capture output to prevent it from cluttering the test results
ob_start();
include 'next_month_template.php';
$output = ob_get_clean();

// Define expected content
$expected_strings = [
    '<h2>Next Month\'s Saints and Readings</h2>',
    '<em>Commemorations:</em>',
];

$all_found = true;
foreach ($expected_strings as $expected) {
    if (strpos($output, $expected) === false) {
        $all_found = false;
        $error_file = __DIR__ . '/test_output_failed.html';
        file_put_contents($error_file, $output);
        echo "Assertion Failed: Did not find expected string '{$expected}' in the output.\n";
        echo "The full output has been saved to: {$error_file}\n";
        break; // Stop on first failure
    }
}

if ($all_found) {
    echo "Test Case 4 PASSED: All expected content was found.\n";
} else {
    echo "Test Case 4 FAILED.\n";
}


// --- Test Case 5: Date with an explanatory note ---
echo "--- Testing explanatory note ---\n";
$_POST['mydate'] = '2026-01-24';

// Capture the output of the included file
ob_start();
include 'daily_template.php';
$output = ob_get_clean();

// Define expected content
$expected_strings = [
    'on this occasion the appointed Gospel for the Liturgy is that for the Fourteenth Sunday of Luke'
];

$all_found = true;
foreach ($expected_strings as $expected) {
    if (strpos($output, $expected) === false) {
        $all_found = false;
        $error_file = __DIR__ . '/test_output_failed.html';
        file_put_contents($error_file, $output);
        echo "Assertion Failed: Did not find expected string '{$expected}' in the output.\n";
        echo "The full output has been saved to: {$error_file}\n";
        break; // Stop on first failure
    }
}

if ($all_found) {
    echo "Test Case 5 PASSED: All expected content was found.\n";
} else {
    echo "Test Case 5 FAILED.\n";
}

echo "\n";

?>
