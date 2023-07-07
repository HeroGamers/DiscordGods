FROM python:3.11-alpine

RUN apk update
RUN apk add --no-cache gcc musl-dev mariadb-dev

WORKDIR /usr/src/app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
