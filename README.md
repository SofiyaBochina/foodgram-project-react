# Foodgram Project
Учебный проект "Продуктовый помощник".

## Как запустить проект:
В командной строке клонируйте проект в нужную папку:
```
git clone https://github.com/SofiyaBochina/foodgram-project-react
```
Перейдите в директорию backend/foodgram/ в проекте:
```
cd backend/foodgram/
```
Выполните миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Соберите статические файлы:
```
python manage.py collectstatic --no-input
```
Запустите проект:
```
python manage.py runserver
```

## Как заполнить базу данными
Импортируете игридиенты:
```
python manage.py import_csv_data ingredients.csv
```
Создайте суперпользователя:
```
python manage.py createsuperuser
```
После этого вы сможете добавлять новые объекты в базу данных через админку проекта по адресу http://127.0.0.1:8000/admin.