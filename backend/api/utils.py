def gen_shopping_list(user):
    '''Метод формирования списка покупок.'''
    ingredients = {}

    shopping_carts = user.shopping_user.all()

    for cart_item in shopping_carts:
        recipe = cart_item.recipe

        for recipe_ingredient in recipe.recipe_ingredients_set.all():
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
