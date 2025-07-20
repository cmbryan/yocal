<?php

function get_db_connection($db_path)
{
    try {
        $db = new PDO('sqlite:' . $db_path);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $db;
    } catch (PDOException $e) {
        // In a real application, you would log this error
        error_log("Database connection failed: " . $e->getMessage());
        return null;
    }
}

function get_data($date_obj)
{
    $yocal_path = __DIR__ . '/../db/YOCal.db';
    $db = get_db_connection($yocal_path);

    if (!$db) {
        return null;
    }

    $year = $date_obj->format('Y');
    $date_str = $date_obj->format('Y-m-d');

    $stmt = $db->prepare("SELECT * FROM Year_{$year} WHERE date = :date");
    $stmt->execute([':date' => $date_str]);

    $result = $stmt->fetch(PDO::FETCH_ASSOC);
    return $result;
}

function get_lections($code)
{
    $yocal_master_path = __DIR__ . '/../db/YOCal_Master.db';
    $db = get_db_connection($yocal_master_path);

    if (!$db) {
        return null;
    }

    $stmt = $db->prepare("SELECT * FROM yocal_lections WHERE code = :code");
    $stmt->execute([':code' => $code]);

    $result = $stmt->fetch(PDO::FETCH_ASSOC);
    return $result;
}

function get_date_from_request($year, $month, $day)
{
    try {
        $date_obj = new DateTime("$year-$month-$day");
        return _get_date($date_obj);
    } catch (Exception $e) {
        return ['error' => 'Invalid date provided.'];
    }
}

function get_today()
{
    $date_obj = new DateTime();
    return _get_date($date_obj);
}

function liturgy_allowed($a_code)
{
    return $a_code[0] == 'G' && ($a_code[2] != 'S' || in_array($a_code, ["G7Sat", "E36Wed", "E36Fri"]));
}

function _get_date($date_obj)
{
    $data = get_data($date_obj);

    if (!$data) {
        return ['error' => 'No data found for ' . $date_obj->format('Y-m-d')];
    }

    $desig_a = $data['desig_a'];
    $desig_g = $data['desig_g'];
    $desig = ($desig_a && $desig_g) ? "{$desig_a}, {$desig_g}" : ($desig_a ?: '');

    $result = [
        'day_name' => $data['day_name'],
        'day_ord' => $data['ord'],
        'month' => $data['month'],
        'year' => $data['year'],
        'fast' => $data['fast'],
        'tone' => $data['tone'],
        'eothinon' => $data['eothinon'],
        'liturgy' => $data['basil'] ?: (liturgy_allowed($data['a_code']) ? '' : 'Liturgy of St John Chrysostom'),
        'desig' => $desig,
        'commem' => $data['major_commem'],
        'fore_after' => $data['fore_after'],
        'global_saints' => $data['class_5'],
        'british_saints' => $data['british'],
    ];

    $a_code = $data['a_code'];
    $g_code = ($data['g_code'] !== $a_code) ? $data['g_code'] : null;

    $a_data = ['lect_1' => null, 'text_1' => null, 'lect_2' => null, 'text_2' => null, 'primary' => []];
    $g_data = $a_data;
    $c_data = $a_data;
    $x_data = $a_data;

    if ($a_code) {
        $a_data = get_lections($a_code);
        $a_data['primary'] = [];
    }

    if ($g_code) {
        $g_data = get_lections($g_code);
        $g_data['primary'] = [];
    }

    if ($data['x_code']) {
        $x_data = get_lections($data['x_code']);
        $x_data['primary'] = [];
    }

    if ($data['c_code']) {
        $c_data = get_lections($data['c_code']);
        $c_data['primary'] = [];
    }

    // Commemorations
    if ($data['c_code']) {
        // Primary lect 1
        if ($data['is_comm_apos']) {
            $c_data['primary'][] = 'lect_1';
        } elseif ($a_code) {
            $a_data['primary'][] = 'lect_1';
        }

        // Primary lect 2
        if ($data['is_comm_gosp']) {
            $c_data['primary'][] = 'lect_2';
        } elseif ($a_code && $a_data['lect_2']) {
            $a_data['primary'][] = 'lect_2';
        } elseif ($g_code && $g_data['lect_2']) {
            $g_data['primary'][] = 'lect_2';
        }
    } else {
        $a_data['primary'][] = 'lect_1';
        if ($a_data['lect_2']) {
            $a_data['primary'][] = 'lect_2';
        } elseif ($g_data['lect_2']) {
            $g_data['primary'][] = 'lect_2';
        }
    }

    if (liturgy_allowed($a_code)) {
        foreach ([$a_data, $g_data, $c_data, $x_data] as &$section) {
            $section['primary'] = [];
        }
        unset($section);
    }

    $result['lections'] = ['basic' => [], 'commem' => [], 'liturgy' => []];
    $result['texts'] = ['basic' => [], 'commem' => []];

    for ($i = 1; $i <= 2; $i++) {
        $lect_idx = "lect_{$i}";
        $text_idx = "text_{$i}";

        foreach ([$a_data, $g_data] as $d) {
            if ($d[$lect_idx]) {
                $result['lections']['basic'][] = $d[$lect_idx];
                $result['texts']['basic'][] = $d[$text_idx];
                if (in_array($lect_idx, $d['primary'])) {
                    $result['lections']['liturgy'][] = $d[$lect_idx];
                }
            }
        }

        foreach ([$c_data, $x_data] as $d) {
            if ($d[$lect_idx]) {
                $result['lections']['commem'][] = $d[$lect_idx];
                $result['texts']['commem'][] = $d[$text_idx];
                if (in_array($lect_idx, $d['primary'])) {
                    $result['lections']['liturgy'][] = $d[$lect_idx];
                }
            }
        }
    }

    return $result;
}

require_once __DIR__ . '/vendor/autoload.php';

function render_template($template_path, $data) {
    $loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
    $twig = new \Twig\Environment($loader, [
        'debug' => true,
        'autoescape' => false,
    ]);
    $twig->addExtension(new \Twig\Extension\DebugExtension());

    // Add the embolden_liturgy_lects function to Twig
    $twig->addFunction(new \Twig\TwigFunction('embolden_liturgy_lects', function ($lect, $liturgy_lects) {
        return in_array($lect, $liturgy_lects) ? "<b>{$lect}</b>" : $lect;
    }));

    $twig->addFilter(new \Twig\TwigFilter('print_r', function ($value) {
        return print_r($value, true);
    }));

    return $twig->render(basename($template_path), $data);
}