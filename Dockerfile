FROM python:3.11-slim

RUN apt-get update

RUN apt-get install ffmpeg libsm6 libxext6  -y && apt install -y git

WORKDIR /app

# Copy over requirements and install first. 
# That  way the layer is unchanged due to code changes. Faster rebuilds
COPY BeckerChecklistApp/requirements.txt .

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY BeckerChecklistApp .

RUN cd BeckerChecklistApp

CMD python manage.py migrate \
    && python manage.py collectstatic --noinput \
    && python manage.py ensure_superuser \
    && exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --max-requests 1000 --timeout 30 BeckerChecklistApp.wsgi:application

