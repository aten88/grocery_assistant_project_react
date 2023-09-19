[![Foodgram Project React workflow](https://github.com/aten88/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/aten88/foodgram-project-react/actions/workflows/main.yml)


Описание проекта:
Продуктовый помощник Foodgram который позволяет:
- Регистрироваться на сайте
- Авторизовываться в качестве пользователя
- Создавать рецепты
- Редактировать рецепты
- Удалять свои рецепты
- Просматривать рецепты других пользователей
- Добавлять рецепты других пользователей в Избранное
- Подписываться на публикации других авторов
- Добавлять рецепты в список покупок и скачивать суммарный список продуктов для их приготовления

Технологии которые применялись в данном проекте:
Python 3.9
Django 3.2.3
Django REST framework 3.12.4
JavaScript
Docker
Github Actions

Структура и технические параметры проекта:

  Весь проект состоит из контейнеров обьединенных в одну единую сеть.
  - Бэкенд проекта расположен в контейнере foodgram_backend и привязан к порту 8000. 
    Работа этого контейнера не останавливается после запуска.
    Данный контейнер взаимодействует с контейнером БД и volumes: foodgram-project-react_media и foodgram-project-react_static

  - Фронтенд проекта расположен в контейнере foodgram_frontend, его задача при старте скопировать статику для запуска проекта
    и поместить ее в папку связанную с volume foodgram-project-react_static. Затем остановить свою работу.

  - Контейнер Gateway перераспределяет запросы между остальными контейнерами. И является "входными воротами проекта".

  - Контейнер БД обрабатывает запросы при обращении к БД, работает в паре с контейнером бэкенда и volume: foodgram-db

  Файлы для обьединения контейнеров в сеть называются "COMPOSE":
  Данные файлы-инструкции описывают порядок и правила выполнения построения и обьединения контейнеров в единую сеть,
  иначе можно сказать отвечают за "ОРКЕСТРАЦИЮ" проекта. В проекте могут быть использованы несколько видов этих файлов:
   - Темплейт-файлы (Template files): Темплейт-файлы используются для создания динамических страниц или документов.
   - Продакшн-файлы (Production files): Продакшн-файлы представляют собой оптимизированные и готовые к развертыванию файлы, 
     которые используются в окружении реального проекта на боевом сервере или в продакшен.
   - Компоуз-файлы без суффикса: Это может быть общее название для файлов, которые не имеют конкретной роли или суффикса.
     Это файлы как правило необходимые в процессе разработки и для разработчиков.

  Дополнительные файлы для запуска проекта:
   - Заполненный файл .env на основе файла .env.example(в корне проекта)
   - Заполненный файл .env на основе файла .env.example(в папке backend) в нем ключ Django
     Данный файл содержит список КОНСТАНТ необходимых для создания контейнеров и запуска проекта.

Как работать с проектом:

Склонировать репозиторий:
  -git clone git@github.com:aten88/foodgram-project-react.git

  Чтобы запустить проект (локально) в контейнерах:

    Создать и заполнить файл .env в корне проекта:
      В переменные необходимо передать константы для создания пользователя БД
      Описание всех переменных есть в файле env.example в корне проекта

    Запустить сборку контейнеров и обьединить их в сеть:
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

    Создать суперпользователя:
    - docker compose exec backend python manage.py createsuperuser

    Перейти по адресу:
    - http://localhost:8000/signin
    - Зарегистрировать нового пользователя
    - Войти с учетными данными
    - Создать рецепт

    Остановка контейнеров:
      В терминале, где был запуск, нажать Ctrl+С или в другом окне терминала:
      - sudo docker compose -f docker-compose.yml down эта команда остановит и удалит все контейнеры и сети.

  
  Для запуска проекта в контейнерах на сервере необходимо:

    Склонировать репозиторий:
      git clone git@github.com:aten88/kittygram_final.git

    В своем аккаунте на GitHub в разделе GitHub Actions Secrets передаем в secrets необходимые значения для запуска:
      ENV_SECRET: DJANGO_KEY = 'django-insecure-yuvxxxxxxxx_xxxxxxx_xxxxxxx'
                  POSTGRES_USER=someuser@somedomain.com
                  POSTGRES_PASSWORD=SecretPassword123
                  POSTGRES_DB=name_db
                  DB_HOST=name_db
                  DB_PORT=someportnumber
                  ALLOWED_HOSTS=xxx.xxx.xx.xx,xxx.x.x.x,localhost,some-domain.net
                  DEBUG=Boolean_Value

    - Переменные для доступа к DockerHub:
      DOCKER_USERNAME = 'Loginusername' - логин.
      DOCKER_PASSWORD = 'Examplepassword+123' пароль.

    - Переменные для подключению к серверу:
      HOST ='77.777.7777.77' - ip адрес сервера.
      USER ='some_username' - логин пользователя сервера.
      SSH_KEY ='SOME??????77777&&&&&XXXXXKEY'- закрытый SSH ключ.
      SSH_PASSPHRASE ='sOmePassword'- пароль.

    - Переменные для отчета в Telegram:
      TELEGRAM_TO ='1234567890' - ID аккаунта Telegram.
      TELEGRAM_TOKEN ='SOME??????77777&&&&&XXXXXTOKEN' - Токен телеграмм-бота.

    Пушим проект в ветку master, ждем выполнения сценария,
    отчета в телеграмм об успешном выполнении, проверяем доступность проекта.


    Развернутый проект доступен по адресу: https://aten-foodgram.redirectme.net/

Автор:
Алексей Тен