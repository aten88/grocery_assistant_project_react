Как работать с проектом:

Склонировать репозиторий:
  -git clone git@github.com:aten88/foodgram-project-react.git

  Чтобы запустить проект локально в контейнерах:

    Создать и заполнить файл .env в корне проекта:
      В переменные необходимо передать константы для создания пользователя БД
      Описание всех переменных есть в файле env.example в корне проекта

    Запустить сборку контейнеров и обьеденить их в сеть:
      - docker compose up

      Применить миграции в отдельном терминале ввести команду:
        - docker compose exec backend python manage.py migrate

      Собрать статику в отдельном терминале ввести команду::
        - docker compose exec backend python manage.py collectstatic
     Скопировать статику в Volume:
        - docker compose exec backend cp -r /app/collected_static/. /backend_static/static/

    Загрузить теги и ингредиенты в БД:
      При запущенном контейнере backend в новом терминале последовательно выполнить команды:
        - docker compose exec backend python manage.py load_tags
        - docker compose exec backend python manage.py load_ingredients

    Перейти по адресу:
    - http://localhost:8000/signin
    - Зарегистрировать нового пользователя
    - Войти с учетными данными
    - Создать рецепт