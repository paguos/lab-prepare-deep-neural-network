# keview-api

## Requirements

- [docker](https://docs.docker.com/get-docker/)
- [python](https://www.python.org/downloads/)
- [pipenv](https://github.com/pypa/pipenv): python depedency manager

To install the depencies run the following command:

```sh
pipenv install --dev --skip-lock
```


## Run

To run locally:

```sh
make run
```

To run with docker:
```sh
make build
docker run -p 8000:8000 keview-api
```

Open the following URL on your web browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Tests

Run lint tests:
```sh
pipenv run flake8
```

Run unit tests:
```sh
make test
```
