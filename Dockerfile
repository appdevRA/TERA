FROM python:3.9

ENV APP_HOME /app
WORKDIR $APP_HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY main/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV BASE_DIR /app/main
WORKDIR $BASE_DIR

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 main.wsgi:application
