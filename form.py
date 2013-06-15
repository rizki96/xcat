#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-05-29 15:08:04
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

__all__ = [  
    'Form',
    'fields',
    'validators',
    'widgets',
    'ValidationError'
]
import re
import types
import tornado.locale
from tornado.escape import to_unicode
from wtforms import Form as wtForm, fields, validators, widgets, ValidationError
from wtforms.compat import iteritems

class Form(wtForm):
    """
    Using this Form instead of wtforms.Form

    Example::

        class SigninForm(Form):
            email = EmailField('email')
            password = PasswordField('password')

        class SigninHandler(RequestHandler):
            def get(self):
                form = SigninForm(self.request.arguments, locale_code=self.locale.code)

    """
    def __init__(self, formdata=None, obj=None, prefix='', locale_code='en_US', **kwargs):
        self._locale_code = locale_code
        super(Form, self).__init__(formdata, obj, prefix, **kwargs)

    def process(self, formdata=None, obj=None, **kwargs):
        if formdata is not None and not hasattr(formdata, 'getlist'):
            formdata = TornadoArgumentsWrapper(formdata)
        super(Form, self).process(formdata, obj, **kwargs)

    
    def load_data(self, obj):
        formdata = TornadoArgumentsWrapper(MopeeObjWrapper(obj, self))
        return self.process(formdata)


    def _get_translations(self):
        if not hasattr(self, '_locale_code'):
            self._locale_code = 'en_US'
        return TornadoLocaleWrapper(self._locale_code)

def MopeeObjWrapper(obj, form):
    data = {}
    model = obj
    if type(obj) is types.DictType:
        for field in form._fields: 
            if model.has_key(field):
                value = model.get(field)
                if type(value) is types.ListType:
                    data[field] = value
                else:
                    data[field] = [ str(value) ]
    else:
        for field in form._fields: 
            if hasattr(model, field):
                value = getattr(model,field)
                if type(value) is types.ListType:
                    data[field] = value
                else:
                    data[field] = [ str(value) ]
    return data


class TornadoArgumentsWrapper(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError

    def getlist(self, key):
        try:
            values = []
            for v in self[key]:
                if type(v) is types.StringType:
                    v = to_unicode(v)
                if isinstance(v, unicode):
                    v = re.sub(r"[\x00-\x08\x0e-\x1f]", " ", v)
                values.append(v)
            return values
        except KeyError:
            raise AttributeError


class TornadoLocaleWrapper(object):
    def __init__(self, code):
        self.locale = tornado.locale.get(code)

    def gettext(self, message):
        return self.locale.translate(message)

    def ngettext(self, message, plural_message, count):
        return self.locale.translate(message, plural_message, count)
