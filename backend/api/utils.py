from recipes. models import ShoppingCart, RecipeIngredient


def gen_shopping_list(user):
    '''Метод формирования списка покупок.'''
    ingredients = {}
    for item in ShoppingCart.objects.filter(user=user):
        recipe = item.recipe
        for recipe_ingredient in RecipeIngredient.objects.filter(
            recipe=recipe
        ):
            ingredient = recipe_ingredient.ingredient
            ingredient_name = ingredient.name
            ingredient_amount = recipe_ingredient.amount
            ingredient_measurement_unit = ingredient.measurement_unit

            key = f'{ingredient_name} ({ingredient_measurement_unit})'
            if key in ingredients:
                ingredients[key] += ingredient_amount
            else:
                ingredients[key] = ingredient_amount

    return ingredients
