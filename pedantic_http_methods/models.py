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
