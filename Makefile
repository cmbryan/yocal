db-build:
	cd db && ./build.sh

php-test:
	# This confirms that the database is working, and also that the webpage display is working
	cd wp_plugin && php tests.php
	cd api-php && YOCAL_DB_DIR="../db/yocal" php test_api.php

# .venv:
# 	rm -rf .venv && \
# 	python -m venv .venv && \
# 	. .venv/bin/activate && \
# 	python -m pip install -r requirements.txt && \
# 	python -m pip install -r requirements_dev.txt
# 
# api-debug: .venv
# 	. .venv/bin/activate && \
# 	python -m flask --app api.api --debug run
# 
# api-production: .venv
# 	. .venv/bin/activate && \
# 	python -m gunicorn 'api.api:app'
# 
# api-test: .venv
# 	. .venv/bin/activate && \
# 	python -m pytest -v
