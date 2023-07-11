Как работать с проектом:

Склонировать репозиторий:

git clone git@github.com:aten88/foodgram-project-react.git

Установить venv:
py -3.9 -m venv venv

Активировать виртуальное окружение:
source venv/Scripts/activate

Обновить пакетный менеджер pip:
python.exe -m pip install --upgrade pip

Установить зависимости:
pip install -r requirements.txt

Создать и применить миграции:
python manage.py makemigrations
python manage.py migrate

Добавить суперюзера:
python manage.py createsuperuser

Запустить проект:
python manage.py runserver

Добавить данные в БД:
Через админку или через API