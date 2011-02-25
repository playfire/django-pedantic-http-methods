"""
:mod:`django-pedantic-http-methods`
===================================

This `Django <http://www.djangoproject.com/>`_ application enforces correct (at
least better) usage of HTTP by raising an exception when performing ``UPDATE``
or ``INSERT`` statements during ``GET`` or ``HEAD`` HTTP requests.

This can be good programming style but also necessary to permit architectures
involving read-write splitting on HTTP method.

Installation
------------

Add ``pedantic_http_methods`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'pedantic_http_methods',
        ...
    )

Configuration
-------------

``PEDANTIC_HTTP_METHODS_ENABLED``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``settings.DEBUG``

To avoid the overheard of checking the request method in some environments, you
can completely disable this application using this setting.

``PEDANTIC_HTTP_METHODS_IGNORE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``()`` (empty)

An iterable of regular expressions that are matched against SQL to be executed.
If any of the patterns match, the SQL is assumed to be side-effect free.

This can be used to ignore tables that are not written to in some environments.
(eg. ``django_session`` only used locally) or to ignore features on your site
that have not or will not be ported to use the correct HTTP method.

Links
-----

View/download code
  https://github.com/playfire/django-pedantic-http-methods

File a bug
  https://github.com/playfire/django-pedantic-http-methods/issues
"""

import re
import sys

from django.http import HttpRequest
from django.db.backends import util, BaseDatabaseWrapper

import app_settings

re_select = re.compile(r'\s*SELECT ', re.IGNORECASE)

class IncorrectHTTPMethod(Exception):
    def __init__(self, sql):
        super(IncorrectHTTPMethod, self).__init__(
            "The current view was requested using a HTTP method "
            "which is incompatible with executing: %s" % sql,
        )

class CursorWrapper(util.CursorDebugWrapper):
    def execute(self, sql, *args, **kwargs):
        if re_select.match(sql):
            return self.cursor.execute(sql, *args, **kwargs)

        for pattern in app_settings.IGNORE:
            if pattern.search(sql.strip()):
                return self.cursor.execute(sql, *args)

        f = sys._getframe()
        while f:
            request = f.f_locals.get('request')
            if isinstance(request, HttpRequest):
                if request.method in ('GET', 'HEAD'):
                    raise IncorrectHTTPMethod(sql)
                break
            f = f.f_back
        del f

        return self.cursor.execute(sql, *args, **kwargs)

if app_settings.ENABLED:
    old_cursor = BaseDatabaseWrapper.cursor
    def cursor(self, *args, **kwargs):
        return CursorWrapper(old_cursor(self, *args, **kwargs), self)
    BaseDatabaseWrapper.cursor = cursor
