import json
from decimal import Decimal
import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки данных из JSON и CSV в БД."""

    def handle(self, *args, **options):
        """Метод загрузки данных из JSON и CSV."""
        with open('data/ingredients.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for item in data:
                Ingredient.objects.create(
                    name=item['name'],
                    amount=Decimal(item.get('amount', 0)),
                    measurement_unit=item['measurement_unit'],
                )
        self.stdout.write(
            self.style.SUCCESS('Успешная загрузка данных из JSON.')
        )
        with open('data/ingredients.json', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                Ingredient.objects.create(
                    name=row['name'],
                    amount=Decimal(row.get('amount', 0)),
                    measurement_unit=row['measurement_unit'],
                )
        self.stdout.write(
            self.style.SUCCESS('Успешная загрузка данных из CSV.')
        )
