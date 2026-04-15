<?php

declare(strict_types=1);

require_once __DIR__ . "/lib.php";

[$yocalPath, $masterPath] = db_paths();
$db = connect_sqlite($yocalPath);
$masterDb = connect_sqlite($masterPath);

function assert_true(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$june11 = get_date_data($db, $masterDb, new DateTimeImmutable("2025-06-11"));
assert_true($june11["year"] === 2025, "June 11 year mismatch");
assert_true($june11["month"] === "June", "June 11 month mismatch");
assert_true($june11["day_ord"] === "11th", "June 11 day ordinal mismatch");
assert_true($june11["lections"]["basic"] === ["Romans 1:18-27", "Matthew 5:20-26"], "June 11 basic lections mismatch");
assert_true($june11["lections"]["commem"] === ["Acts 11:19-30", "Luke 10:16-21"], "June 11 commem lections mismatch");
assert_true($june11["lections"]["liturgy"] === ["Acts 11:19-30", "Matthew 5:20-26"], "June 11 liturgy lections mismatch");

$june12 = get_date_data($db, $masterDb, new DateTimeImmutable("2025-06-12"));
assert_true($june12["lections"]["basic"] === ["Romans 1:28-2:9", "Matthew 5:27-32"], "June 12 basic lections mismatch");
assert_true($june12["lections"]["commem"] === [], "June 12 commem lections should be empty");
assert_true($june12["lections"]["liturgy"] === $june12["lections"]["basic"], "June 12 liturgy should match basic");

echo "All PHP API tests passed.\n";
