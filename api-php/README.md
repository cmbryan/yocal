# YOCal PHP API

PHP version of the YOCal API using SQLite and the built-in PHP server.

## Requirements

- PHP 8.1+
- SQLite extension enabled for PHP
- Existing database files:
  - `db/yocal/YOCal.db`
  - `db/yocal/YOCal_Master.db`

## Database path configuration

By default, the API resolves DB files from:

- `../wp/wp-content/uploads/yocal/YOCal.db`
- `../wp/wp-content/uploads/yocal/YOCal_Master.db`

This matches a typical WordPress upload location and requires no environment setup.

If your DB folder is elsewhere, set one variable:

- `YOCAL_DB_DIR` (directory containing both DB files)

Example:

`YOCAL_DB_DIR=/var/www/shared/yocal php -S 127.0.0.1:8000 -t api-php api-php/index.php`

## Run

For local development with DBs in `db/yocal`, use:

```bash
bash api-php/run-local.sh
```

Then open:

- `http://127.0.0.1:8000/test`
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/date?year=2025&month=6&day=11`
- `http://127.0.0.1:8000/test-display?year=2025&month=6&day=11`

## Test logic

Run:

```bash
php api-php/test_api.php
```

This checks the same June 11/12, 2025 cases as the Python and JS versions.

## Files

- `api-php/index.php`: route handling and HTTP responses
- `api-php/lib.php`: data access and date/lection assembly logic
- `api-php/template.php`: HTML view used by `/test-display`
- `api-php/test_api.php`: lightweight parity checks

## Uploading to Production

This is handled automatically by [Github Actions](../.github/workflows/main.yml). However, note that `.htaccess` and `*.sh` are excluded because they are blocked from upload by the host fol security reasons.
