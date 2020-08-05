build:
	docker build . -t keview-api
	# docker run -p 8000:8000 keview-api

run:
	pipenv install --skip-lock
	pipenv run uvicorn keview.api:app --reload

example:
	pipenv install --skip-lock
	PYTHONPATH=./ pipenv run python examples/example.py

test: build
	docker-compose up -d
	sleep 10
	pipenv run pytest
	docker-compose down -v
