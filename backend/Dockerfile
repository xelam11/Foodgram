FROM python:3.8.5
WORKDIR /code
COPY . .
RUN pip3 install -r requirements.txt
CMD gunicorn foodgram_api.wsgi:application --bind 0:8000