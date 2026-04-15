<?php
declare(strict_types=1);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Display</title>
</head>
<body>
    <h1>Test Display</h1>
    <p>
        <h2><?= $data["day_name"] ?> <?= $data["day_ord"] ?> <?= $data["month"] ?> <?= $data["year"] ?></h2>
        <?php if (!empty($data["fast"])): ?>
            <?= $data["fast"] ?>
        <?php endif; ?>
        <?php if (!empty($data["commem"])): ?>
            <br/>
            <h3><?= $data["commem"] ?></h3>
        <?php endif; ?>
        <?php if (!empty($data["fore_after"])): ?>
            <br/>
            <h3><?= $data["fore_after"] ?></h3>
        <?php endif; ?>
        <?php if (!empty($data["tone"])): ?>
            <br/>
            <?= $data["tone"] ?>&mdash;<?= $data["eothinon"] ?>
        <?php endif; ?>
        <?php if (!empty($data["tone"])): ?>
            <br/>
            <?= $data["tone"] ?>&mdash;<?= $data["eothinon"] ?>
        <?php endif; ?>
        <?php if (!empty($data["liturgy"])): ?>
            <br/>
            <?= $data["liturgy"] ?>
        <?php endif; ?>
        <h3><?= $data["desig"] ?></h3>
    </p>
    <p>
        <em>Today we commemorate:</em>
        <br/>
        <?= $data["global_saints"] ?>
        <br/>
        <em>British Isles and Ireland:</em>
        <br/>
        <?= $data["british_saints"] ?>
    </p>
    <p>
        <em>Today's readings:</em>
        <?php foreach ($data["lections"]["basic"] as $idx => $lect): ?>
            <br/>
            <?php if (!empty($data["lections"]["commem"])): ?>
                <?= in_array($lect, $data["lections"]["liturgy"], true) ? "<b>{$lect}</b>" : $lect ?><?= $idx < count($data["lections"]["basic"]) - 1 ? "; " : "" ?>
            <?php else: ?>
                <?= $lect ?><?= $idx < count($data["lections"]["basic"]) - 1 ? "; " : "" ?>
            <?php endif; ?>
        <?php endforeach; ?>

        <?php if (!empty($data["lections"]["commem"])): ?>
            <br/>
            <em>For the commemmoration:</em>
            <?php foreach ($data["lections"]["commem"] as $idx => $lect): ?>
                <br/>
                <?= in_array($lect, $data["lections"]["liturgy"], true) ? "<b>{$lect}</b>" : $lect ?><?= $idx < count($data["lections"]["commem"]) - 1 ? "; " : "" ?>
            <?php endforeach; ?>
        <?php endif; ?>
        <?php if (!empty($data["liturgy"]) && !empty($data["lections"]["commem"])): ?>
            <br/>
            <em>Readings in <b>bold type</b> are those appointed by the Typikon for use at the Liturgy</em>
        <?php endif; ?>
    </p>
    <p>
        <?php foreach ($data["texts"]["basic"] as $text): ?>
            <?= $text ?>
            <br/>
        <?php endforeach; ?>
        <?php foreach ($data["texts"]["commem"] as $text): ?>
            <?= $text ?>
            <br/>
        <?php endforeach; ?>
    </p>
</body>
</html>
