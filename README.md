Как работать с проектом:

Склонировать репозиторий:
  -git clone git@github.com:aten88/foodgram-project-react.git

  Заполнить файл .env:
    В переменные необходимо передать значения для создания пользователя и БД
    Описание всех переменных есть в файле env.example

  Собрать статику:
  ???
  ???

  Загрузить теги и ингредиенты в БД:
    При запущенном контейнере backend в новом терминале последовательно выполнить команды:
      -docker compose exec backend python manage.py load_tags
      -docker compose exec backend python manage.py load_ingredients

Запустить проект:
