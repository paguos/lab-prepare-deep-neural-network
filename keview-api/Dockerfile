FROM python:3.8.3-slim-buster

RUN pip install pipenv

WORKDIR keview-api
COPY . .

RUN pipenv install --system --skip-lock

CMD ["uvicorn", "keview.api:app", "--host", "0.0.0.0"]