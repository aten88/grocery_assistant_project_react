from rest_framework import serializers


def validate_unique_ingredients(ingredients_data):
    '''Метод проверки уникальности ингредиента.'''
    ingredient_ids = set()
    for ingredient_data in ingredients_data:
        ingredient_id = ingredient_data['ingredient']['id']
        if ingredient_id in ingredient_ids:
            raise serializers.ValidationError(
                'Создание рецепта с одинаковыми ингредиентами невозможно.'
            )
        ingredient_ids.add(ingredient_id)
    return ingredients_data


def validate_tags(tags):
    '''Метод проверки наличия тега.'''
    if not tags:
        raise serializers.ValidationError(
            'Создание рецепта без тегов невозможно.'
        )
    return tags


def validate_unique_tags(tags):
    '''Метод проверки что тег уникален.'''
    tag_ids = [tag.id for tag in tags]
    if len(tag_ids) != len(set(tag_ids)):
        raise serializers.ValidationError(
            'Создание рецепта с одинаковыми тегами невозможно.'
        )
    return tags
