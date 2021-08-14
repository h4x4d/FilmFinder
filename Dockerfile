FROM python:3.9-slim-buster

EXPOSE 80

WORKDIR /app

ARG TELEGRAMBOT_TOKEN
ENV TELEGRAMBOT_TOKEN=$TELEGRAMBOT_TOKEN

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "-m" , "flask", "run", "-h", "0.0.0.0", "-p", "80"]
