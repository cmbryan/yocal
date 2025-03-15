db-build:
	cd db && ./build.sh

api-debug:
	flask --app api.api --debug run
