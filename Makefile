db-build:
	cd db && ./build.sh

.venv:
	python -m venv .venv && \
	. .venv/bin/activate && \
	python -m pip install -r requirements.txt && \
	python -m pip install -r requirements_dev.txt

api-python-debug: .venv
	. .venv/bin/activate && \
	python -m flask --app api_python.api --debug run

api-python-production: .venv
	. .venv/bin/activate && \
	python -m gunicorn 'api_python.api:app'

api-python-test: .venv
	. .venv/bin/activate && \
	python -m pytest -v

api-php-test:
	make -C api_php run-unit-tests
