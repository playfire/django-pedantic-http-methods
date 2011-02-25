import re

from django.conf import settings

ENABLED = getattr(settings, 'PEDANTIC_HTTP_METHODS_ENABLED', settings.DEBUG)

IGNORE = [
    re.compile(x) for x in getattr(settings, 'PEDANTIC_HTTP_METHODS_IGNORE', ())
]
