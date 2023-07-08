import csv

from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILES_DIR
from recipes.models import Tag


# python3 manage.py utils - команда для загрузки ингредиентов

class Command(BaseCommand):
    """Команда для загрузки тегов в базу данных."""

    help = 'Загрузка тегов в базу данных.'

    def handle(self, *args, **kwargs):
        with open(
                f'{CSV_FILES_DIR}/tags.csv', encoding='utf-8'
        ) as file:
            csv_reader = csv.reader(file, delimiter=',', quotechar='"')
            for row in csv_reader:
                name = row[0]
                color = row[1]
                slug = row[2]
                Tag.objects.create(
                    name=name, color=color, slug=slug
                )
        print('Теги в базу данных загружены.')
        print('ADD', Tag.objects.count(), 'tags')
