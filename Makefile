db-build:
	cd db && ./build.sh

.venv:
	rm -rf .venv && \
	python -m venv .venv && \
	. .venv/bin/activate && \
	python -m pip install -r requirements.txt && \
	python -m pip install -r requirements_dev.txt

api-debug: .venv
	. .venv/bin/activate && \
	python -m flask --app api.api --debug run

api-production: .venv
	. .venv/bin/activate && \
	python -m gunicorn 'api.api:app'

api-test: .venv
	. .venv/bin/activate && \
	python -m pytest -v
