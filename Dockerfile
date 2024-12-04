FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install pipenv

RUN pipenv install --system --deploy

CMD ["pyton", "main.py"]
