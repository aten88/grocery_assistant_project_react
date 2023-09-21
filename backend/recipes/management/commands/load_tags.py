import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    '''Команда для загрузки данных о тегах из CSV в БД.'''
    help = 'Загрузка данных тегов из CSV файла'

    def handle(self, *args, **kwargs):
        csv_file_path = 'data/tags.csv'

        with open(csv_file_path, encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                name = row[0]
                color = row[1]
                slug = row[2]

                tag, created = Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug,
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Тег "{name}" успешно создан.')
                    )

            self.stdout.write(
                self.style.SUCCESS('Успешная загрузка данных из CSV.')
            )
