![example workflow](https://github.com/SofiyaBochina/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Foodgram Project
Учебный проект "Продуктовый помощник".

## Как запустить проект локально:
В командной строке клонируйте проект в нужную папку:
```
git clone https://github.com/SofiyaBochina/foodgram-project-react
```
Перейдите в директорию infra/ в проекте:
```
cd infra/
```
Запустите контейнеры:
```
docker compose up -d
```
Выполните миграции:
```
docker compose exec -T backend python manage.py makemigrations
docker compose exec -T backend python manage.py migrate
```
Соберите статические файлы:
```
docker compose exec -T backend python manage.py collectstatic --no-input
```

## Как заполнить базу данными
Импортируете игридиенты:
```
docker compose exec -T backend python manage.py import_csv_data ingredients.csv
```
Создайте суперпользователя:
```
docker compose exec -T backend python manage.py createsuperuser
```
После этого вы сможете добавлять новые объекты в базу данных через админку проекта по адресу http://127.0.0.1:8000/admin.

## Документация и данные от суперюзера
В данный момент сервер запущен на сервере 51.250.105.18. Документация доступна по ссылке http://51.250.105.18/api/docs/.

Суперюзер:
```
email: superuser@foodgram.com; password: super_user_1
```

Тестовый пользователь:
```
email: test@foodgram.com; password: test_user_1
```