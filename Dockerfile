FROM python:3.8

RUN apt-get update

RUN apt-get install ffmpeg libsm6 libxext6  -y && apt install -y git

WORKDIR /app

COPY . .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD cd BeckerChecklistApp && python manage.py migrate && python manage.py collectstatic --noinput && exec gunicorn BeckerChecklistApp.wsgi:application -c gunicorn.conf.py
