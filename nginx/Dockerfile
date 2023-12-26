FROM nginx:1.25.3-alpine
RUN rm -r /etc/nginx/conf.d && rm /etc/nginx/nginx.conf && rm /usr/share/nginx/html/*
COPY ./nginx.conf /etc/nginx/