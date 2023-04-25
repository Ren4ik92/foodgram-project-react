# 158.160.46.197
# Foodgram

## Описание

Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. А перед походом в магазин можно скачать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


### Технологии

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

### Особенности

- у неаунтефицированных пользователей доступ к API только на чтение;
- для загрузки проекта применён Docker, подготовлены файлы для развертывания инфраструктуры;
- настроены CI/CD.

### Установка

1. Клонировать репозиторий:

```bash
git clone https://github.com/Ren4ik92/foodgram-project-react
```

2. В директории foodgram-project-react/infra создаём файл .env и записываем в него следующие переменные окружения:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя базы данных>
POSTGRES_USER=<ваш логин для подключения к базе данных>
POSTGRES_PASSWORD=<ваш пароль для подключения к базе данных>
DB_HOST=<название сервиса/контейнера>
DB_PORT=<порт для подключения к базе данных>
SECRET_KEY=<секретный ключ Django>
DEBUG=<True или False>
```

3. В директории foodgram-project-react/infra/ выполняем команду для сборки контейнеров:

```bash
docker compose up -d --build
```

4. Внутри собранных контейнеров собираем статику, создаём и выполняем миграции, загружаем данные и создаём суперпользователя:

```bash
docker compose exec backend python manage.py collectstatic --no-input
docker compose exec backend python manage.py makemigrations 
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py load_data
docker compose exec backend python manage.py createsuperuser
```