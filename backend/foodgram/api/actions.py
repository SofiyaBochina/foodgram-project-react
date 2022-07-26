import datetime as dt
import os
from wsgiref.util import FileWrapper

from django.http import HttpResponse


def download_file(query):
    f_data = []
    for i, ingredient in enumerate(query, 1):
        f_data.append(
            '{}) {} {} {};'.format(
                i,
                ingredient['ingredient__name'],
                ingredient['amount'],
                ingredient["ingredient__measurement_unit"]
            )
        )
    f_text = '\n'.join(f_data)
    basename = 'shopping_cart'
    suffix = dt.datetime.now().strftime("%y%m%d_%H%M%S")
    f_name = "_".join([basename, suffix])
    f = open(f'{f_name}.txt', 'a')
    f.write(f_text)
    f.close()
    f = open(f'{f_name}.txt', 'r')
    response = HttpResponse(
        FileWrapper(f),
        content_type='application/msword'
    )
    response['Content-Disposition'] = (
        'attachment; '
        f'filename="{f_name}.txt"'
    )
    os.remove(f'{f_name}.txt')
    return response
