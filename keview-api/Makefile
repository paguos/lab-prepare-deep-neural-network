docker:
	docker build . -t keview-api
	docker run keview-api

example:
	pipenv install --skip-lock
	PYTHONPATH=./ pipenv run python examples/example.py
