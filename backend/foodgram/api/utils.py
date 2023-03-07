from django.http import HttpResponse


def create_recipe_file(ingredients_in_shopping_cart):
    text = []
    for v in ingredients_in_shopping_cart:
        text.append(
            f"{v['ingredient__name']} - {v['amount']} "
            f"{v['ingredient__measurement_unit']} ")

    text = '\n'.join(text)
    response = HttpResponse(text, content_type='text/plain')
    response['Content-Disposition'] = ('attachment; '
                                       'filename=shoping_cart.txt')
    return response
