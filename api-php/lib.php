<?php

declare(strict_types=1);

function db_paths(): array
{
    // Optional override for deployments. If unset, default to WordPress uploads.
    $dbDir = getenv("YOCAL_DB_DIR") ?: (__DIR__ . "/../wp/wp-content/uploads/yocal");
    $dbDir = rtrim($dbDir, "/");
    $yocal = $dbDir . "/YOCal.db";
    $master = $dbDir . "/YOCal_Master.db";

    if (!file_exists($yocal) || !file_exists($master)) {
        throw new RuntimeException(
            "Required database files not found. Checked: {$yocal} and {$master}"
        );
    }

    return [$yocal, $master];
}

function connect_sqlite(string $path): PDO
{
    $pdo = new PDO("sqlite:" . $path, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
    return $pdo;
}

function liturgy_allowed(?string $aCode): bool
{
    if ($aCode === null || $aCode === "") {
        return false;
    }

    $third = strlen($aCode) > 2 ? $aCode[2] : "";
    return $aCode[0] === "G" && ($third !== "S" || in_array($aCode, ["G7Sat", "E36Wed", "E36Fri"], true));
}

function empty_lections(): array
{
    return [
        "lect_1" => null,
        "text_1" => null,
        "lect_2" => null,
        "text_2" => null,
        "primary" => [],
    ];
}

function get_lections(PDO $db, ?string $code): array
{
    if ($code === null || $code === "") {
        return empty_lections();
    }

    $stmt = $db->prepare("SELECT * FROM yocal_lections WHERE code = :code");
    $stmt->execute([":code" => $code]);
    $row = $stmt->fetch();

    if (!$row) {
        return empty_lections();
    }

    $row["primary"] = [];
    return $row;
}

function get_data(PDO $db, DateTimeImmutable $dateObj): ?array
{
    $year = (int) $dateObj->format("Y");
    $table = "Year_" . $year;

    // Year is integer-derived to avoid SQL injection when interpolating table name.
    $stmt = $db->prepare("SELECT * FROM {$table} WHERE date = :date");
    $stmt->execute([":date" => $dateObj->format("Y-m-d")]);
    $row = $stmt->fetch();

    return $row ?: null;
}

function get_date_data(PDO $db, PDO $masterDb, DateTimeImmutable $dateObj): array
{
    $data = get_data($db, $dateObj);
    if (!$data) {
        return ["error" => "No data found for " . $dateObj->format("Y-m-d")];
    }

    $desigA = $data["desig_a"] ?? "";
    $desigG = $data["desig_g"] ?? "";
    if ($desigA && $desigG) {
        $desig = "{$desigA}, {$desigG}";
    } elseif ($desigA) {
        $desig = $desigA;
    } else {
        $desig = "";
    }

    $aCode = $data["a_code"] ?? null;
    $result = [
        "day_name" => $data["day_name"],
        "day_ord" => $data["ord"],
        "month" => $data["month"],
        "year" => (int) $data["year"],
        "fast" => $data["fast"],
        "tone" => $data["tone"],
        "eothinon" => $data["eothinon"],
        "liturgy" => ($data["basil"] ?? "") !== ""
            ? $data["basil"]
            : (liturgy_allowed($aCode) ? "" : "Liturgy of St John Chrysostom"),
        "desig" => $desig,
        "commem" => $data["major_commem"],
        "fore_after" => $data["fore_after"],
        "global_saints" => $data["class_5"],
        "british_saints" => $data["british"],
    ];

    $gCode = ($data["g_code"] ?? null) !== $aCode ? ($data["g_code"] ?? null) : null;
    $aData = get_lections($masterDb, $aCode);
    $gData = get_lections($masterDb, $gCode);
    $cData = get_lections($masterDb, $data["c_code"] ?? null);
    $xData = get_lections($masterDb, $data["x_code"] ?? null);

    if (!empty($data["c_code"])) {
        if ((int) ($data["is_comm_apos"] ?? 0) === 1) {
            $cData["primary"][] = "lect_1";
        } elseif (!empty($aCode)) {
            $aData["primary"][] = "lect_1";
        }

        if ((int) ($data["is_comm_gosp"] ?? 0) === 1) {
            $cData["primary"][] = "lect_2";
        } elseif (!empty($aCode) && !empty($aData["lect_2"])) {
            $aData["primary"][] = "lect_2";
        } elseif (!empty($gCode) && !empty($gData["lect_2"])) {
            $gData["primary"][] = "lect_2";
        }
    } else {
        $aData["primary"][] = "lect_1";
        if (!empty($aData["lect_2"])) {
            $aData["primary"][] = "lect_2";
        } elseif (!empty($gData["lect_2"])) {
            $gData["primary"][] = "lect_2";
        }
    }

    if (liturgy_allowed($aCode)) {
        foreach ([$aData, $gData, $cData, $xData] as &$section) {
            $section["primary"] = [];
        }
        unset($section);
    }

    $result["lections"] = [
        "basic" => [],
        "commem" => [],
        "liturgy" => [],
    ];
    $result["texts"] = [
        "basic" => [],
        "commem" => [],
    ];

    foreach ([1, 2] as $idx) {
        $lectKey = "lect_" . $idx;
        $textKey = "text_" . $idx;

        foreach ([$aData, $gData] as $section) {
            if (!empty($section[$lectKey])) {
                $result["lections"]["basic"][] = $section[$lectKey];
                $result["texts"]["basic"][] = $section[$textKey];
                if (in_array($lectKey, $section["primary"], true)) {
                    $result["lections"]["liturgy"][] = $section[$lectKey];
                }
            }
        }

        foreach ([$cData, $xData] as $section) {
            if (!empty($section[$lectKey])) {
                $result["lections"]["commem"][] = $section[$lectKey];
                $result["texts"]["commem"][] = $section[$textKey];
                if (in_array($lectKey, $section["primary"], true)) {
                    $result["lections"]["liturgy"][] = $section[$lectKey];
                }
            }
        }
    }

    return $result;
}

function parse_query_date(array $query): ?DateTimeImmutable
{
    if (!isset($query["year"], $query["month"], $query["day"])) {
        return null;
    }

    $year = (int) $query["year"];
    $month = (int) $query["month"];
    $day = (int) $query["day"];

    $date = DateTimeImmutable::createFromFormat("Y-n-j", "{$year}-{$month}-{$day}");
    if ($date === false) {
        return null;
    }
    return $date;
}

