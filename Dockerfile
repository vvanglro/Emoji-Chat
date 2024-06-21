FROM python:3.11.9-slim

WORKDIR /app/emoji-chat
COPY . .

RUN python3 -m pip install -r requirements.txt
CMD python3 main.py

