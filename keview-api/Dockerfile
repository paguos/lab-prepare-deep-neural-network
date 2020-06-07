FROM python:3.8.2-slim-buster

RUN pip install pipenv==2018.11.26

WORKDIR keview-api
COPY . .

RUN pipenv install --system --dev

CMD ["python", "test.py"]