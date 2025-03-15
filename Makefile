db-build:
	cd db && ./build.sh

api-debug:
	python -m flask --app api.api --debug run

api-production:
	python -m gunicorn 'api.api:app'