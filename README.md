Запуск через `docker-compose up`.

Необходимые переменные окружения:

- `SELF_ADDRESS` - адрес сервера, чтобы генерировать Stripe redirect обратно на наш магазин.
- `ALLOWED_HOSTS` - адреса через пробел. Пример: `django-server 127.0.0.1 127.0.0.1:7890`.
- `CSRF_TRUSTED_ORIGINS` - адреса через пробел. Пример: `http://django-server http://127.0.0.1:7890`.
- `DJANGO_SECRET_KEY` - секретный ключ.
- `RUN=1`

Для каждой валюты нужна пара переменных окружения:
- `*_STRIPE_SERVER_API_KEY` - секретный ключ на сервере для доступа к Stripe API.
- `*_STRIPE_CLIENT_API_KEY` - ключ на клиенте для доступа к Stripe API на стороне браузера.

Вместо `*` вставить трехсимвольное обозначение валюты, например `USD_STRIPE_SERVER_API_KEY`.

Эти переменные окружения поместить в `prostye_resheniya/prostye_resheniya/.env` файл. 

Пример файла:
```
USD_STRIPE_SERVER_API_KEY=sk_test_...
USD_STRIPE_CLIENT_API_KEY=pk_test_...
PLN_STRIPE_SERVER_API_KEY=sk_test_...
PLN_STRIPE_CLIENT_API_KEY=pk_test_...
SELF_ADDRESS=http://127.0.0.1:7890
ALLOWED_HOSTS=django-server 127.0.0.1 127.0.0.1:7890
DEBUG=0
CSRF_TRUSTED_ORIGINS=http://django-server http://127.0.0.1:7890
DJANGO_SECRET_KEY=...
RUN=1
```

На сайте есть корзина. Корзина мультивалютная, т. е. каждый товар уходит в свою "подкорзину" в зависимости от валюты.

Если валютных корзин несколько, при переходе в корзину будет предложен выбор валюты.

Соответственно, в зависимости от валюты корзины будет использоваться соответствующая Stripe API Key пара.

В админке по-умолчанию логин:пароль `admin:admin`.