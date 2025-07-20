SHELL=/bin/bash
.PHONY: run-unit-tests install-composer


run-unit-tests: install-composer
	@echo "Running PHPUnit tests..."
	./vendor/bin/phpunit test_*.php


install-composer:
	@echo "Checking for composer..."
	@if ! command -v composer &> /dev/null; then \
		echo "Composer not found. Installing composer..."; \
		php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"; \
		php composer-setup.php --install-dir=/usr/local/bin --filename=composer; \
		rm composer-setup.php; \
	fi
	@echo "Installing composer dependencies..."
	composer install --no-interaction --prefer-dist