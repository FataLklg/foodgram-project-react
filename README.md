[![CI](https://github.com/fatalklg/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/fatalklg/foodgram-project-react/actions/workflows/main.yml)
### Описание проекта:
Проект Foodgram - сайт "Продуктовый помошник", на котором можно публиковать свои рецепты, добавлять чужие в избранное и подписываться на публикации других авторов. Предусмотрена возможность добавления рецептов в "корзину" и дальнейшей выгрузки текстового файла, с подсчётом всех необходимых ингредиентов для добавленных в корзину блюд. Проект развёрнут в докер-контейнерах на облачном сервере яндекса. Проект можно скачать и развернуть локально по инструкции ниже.

*Сайт доступен по адресу:* http://158.160.43.79/
*Администрирование сайта:* http://158.160.43.79/admin/
*Документация по адресу:* http://158.160.43.79/api/docs/

---
#### Ключи доступа:
- **Пользователь:**
*login* - `petrov@test.ru`
*password* - `qwerty123`

- **Администратор:**
*login к сайту* - `admin@admin.ru`
*login к админке* - `admin`
*password* - `admin`
---
#### Разворачиваем проект локально:

- Склонируйте проект на компьютер:
```
git clone https://github.com/FataLklg/foodgram-project-react.git
```
- Перейдите в дирректорию проекта:
```
cd foodgram-project-react/
```
- Создайте и активируйте виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
```
- Обновите модуль pip и установите зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r backend/foodgram/requirements.txt
```
- Перейдите в дирректорию `/infra`:
```
cd infra
```
- Создайте файл `.env` и наполните его содержимым из шаблона:
```
touch .env
# шаблон для наполнения:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432
```
- Установите Docker по инструкции https://docs.docker.com/engine/install/

- Разверните контейнеры в докере:
```
docker-compose up -d
```
- Примените миграции и соберите статику:
```
docker-compose exec back python manage.py migrate
docker-compose exec back python manage.py collectstatic --no-input
```
- Создайте суперпользователя:
```
docker-compose exec back python manage.py createsuperuser
```
*Проект развёрнут и доступен по адресу:*  http://127.0.0.1/

---
### Примеры запросов к api:
- Список пользователей `GET /api/users/`:
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/?page=4",
  "previous": "http://foodgram.example.org/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    }
  ]
}
```
- Профиль пользователя `GET /api/users/{id}/`:
```
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": false
}
```
- Список ингредиентов `GET /api/ingredients/`:
```
[
  {
    "id": 0,
    "name": "Капуста",
    "measurement_unit": "кг"
  }
]
```
- Создание рецепта `POST /api/recipes/`:

*Request:*
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
*Response:*
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```
