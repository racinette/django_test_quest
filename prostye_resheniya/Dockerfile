FROM python:3.10.13-alpine
ARG DJANGO_SUPERUSER_USERNAME=admin
ARG DJANGO_SUPERUSER_PASSWORD=admin
ARG DJANGO_SUPERUSER_EMAIL=admin@admin.admin
ENV RUN=0
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN python manage.py makemigrations && python manage.py migrate
RUN python manage.py createsuperuser --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL --noinput
RUN python manage.py collectstatic
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "prostye_resheniya.wsgi"]
