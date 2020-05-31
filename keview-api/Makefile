docker:
	docker build . -t keview-api
	docker run keview-api

local:
	pipenv install
	pipenv run python test.py
