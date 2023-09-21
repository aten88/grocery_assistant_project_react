import csv
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    '''Команда для загрузки данных из JSON и CSV в БД.'''

    def handle(self, *args, **options):
        '''Метод загрузки данных из JSON и CSV.'''

        with open('data/ingredients.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for item in data:
                name = item['name']
                measurement_unit = item['measurement_unit']

                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )
                if created:
                    self.stdout.write(f'Ингредиент "{name}" успешно создан.')

        self.stdout.write(
            self.style.SUCCESS('Успешная загрузка данных из JSON.')
        )

        with open('data/ingredients.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                name = row[0]
                measurement_unit = row[1]

                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )

                if created:
                    self.stdout.write(f'Ингредиент "{name}" успешно создан.')

        self.stdout.write(
            self.style.SUCCESS('Успешная загрузка данных из CSV.')
        )
