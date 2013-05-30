#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-05-29 15:08:04
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

__all__ = [
    'Length',
    'NumberRange',
    'Required',
    'Regexp',
    'Email',
    'IP',
    'URL',
    'SafeString',
    'FieldBase',
    'Button',
    'Submit',
    'Hidden',
    'Text',
    'Textarea',
    'Select',
    'Checkbox',
    'Radio',
    'Password',
    'Form',
]

import inspect
import re 
from utils import Validators , Filters , Json

'''
表单
'''

# Python 2/3 compat
def with_metaclass(meta, base=object):
    return meta("NewBase", (base,), {})

class Length(object):
    """
    Validates the length of a string.

    :param min:
        The minimum required length of the string. If not provided, minimum
        length will not be checked.
    :param max:
        The maximum length of the string. If not provided, maximum length
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)d` and `%(max)d` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """

    def __init__(self, min=-1, max=-1, message=None):
        assert min != -1 or max!=-1, 'At least one of `min` or `max` must be specified.'
        assert max == -1 or min <= max, '`min` cannot be more than `max`.'
        self.min = min
        self.max = max
        self.message = message

    def get_config(self):
        return {
            'name'    : self.__class__.__name__,
            'message' : self.message,
            'min'     : self.min ,
            'max'     : self.max ,
        }

    def validator(self, form, element):
        l = element.get_value() and len(element.get_value()) or 0
        if l < self.min or self.max != -1 and l > self.max:
            if self.message is None:
                if self.max == -1:
                    self.message = form._('Field must be at least %s character long.') % self.min
                elif self.min == -1:
                    self.message = form._('Field cannot be longer than %s character.' ) % self.max
                else:
                    self.message = form._('Field must be between %s and %s characters long.') % (self.min , self.max) 

            element._on['error'](element , self.message)
            return False
        return True

class NumberRange(object):
    """
    Validates that a number is of a minimum and/or maximum value, inclusive.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param min:
        The minimum required value of the number. If not provided, minimum
        value will not be checked.
    :param max:
        The maximum value of the number. If not provided, maximum value
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)s` and `%(max)s` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """
    def __init__(self, min=None, max=None, message=None):
        self.min = min
        self.max = max
        self.message = message

    def get_config(self):
        return {
            'name'    : self.__class__.__name__,
            'message' : self.message,
            'min'     : self.min ,
            'max'     : self.max ,
        }

    def validator(self, form, element):
        data = element.get_value()
        if data is None or (self.min is not None and data < self.min) or \
            (self.max is not None and data > self.max):
            if self.message is None:
                # we use %(min)s interpolation to support floats, None, and
                # Decimals without throwing a formatting exception.
                if self.max is None:
                    self.message = form._('Number must be greater than %s.') % self.min
                elif self.min is None:
                    self.message = form._('Number must be less than %s.') % self.max
                else:
                    self.message = form._('Number must be between %s and %s.') % (self.min , self.max)

            element._on['error'](element , self.message)
            return False
        return True

class Required(object):
    """
    Validates that the field contains data. This validator will stop the
    validation chain on error.

    :param message:
        Error message to raise in case of a validation error.
    """
  

    def __init__(self, message=None):
        self.message = message

    def get_config(self):
        return {
            'name'    : self.__class__.__name__,
            'message' : self.message,
        }

    def validator(self, form, element):
        data = element.get_value()
        if (not isinstance(data, int) and not data) or \
           isinstance(data, basestring) and not data.strip():
            if self.message is None:
                self.message = form._(u'This field is required.')

            element._on['error'](element , self.message)
            return False
        return True

class Regexp(object):
    """
    Validates the field against a user provided regexp.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    :param flags:
        The regexp flags to use, for example re.IGNORECASE. Ignored if
        `regex` is not a string.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, basestring):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def get_config(self):
        return {
            'name'    : self.__class__.__name__,
            'message' : self.message,
            'regex'   : self.regex.pattern ,
        }

    def validator(self, form, element):
        if not self.regex.match(element.get_value() or ''):
            if self.message is None:
                self.message = form._('Invalid input.')

            element._on['error'](element , self.message)
            return False
        return True

class Email(Regexp):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        super(Email, self).__init__(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE, message)

    def validator(self, form, element):
        if self.message is None:
            self.message = form._('Invalid email address.')

        return super(Email, self).validator(form, element)

class IP(Regexp):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        super(IPAddress, self).__init__(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', message=message)

    def validator(self, form, element):
        if self.message is None:
            self.message = form._('Invalid IP address.')

        return super(IPAddress, self).validator(form, element)

class URL(Regexp):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        super(URL, self).__init__(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', message=message)

    def validator(self, form, element):
        if self.message is None:
            self.message = form._('Invalid URL address.')

        return super(URL, self).validator(form, element)

class SafeString(Regexp):
    """ 安全字符 """
    def __init__(self, message=None):
        super(SafeString, self).__init__(r'^\w+$', message=message)

    def validator(self, form, element):
        if self.message is None:
            self.message = form._('Illegal characters.')

        return super(SafeString, self).validator(form, element)


class FieldBase(object):
    """ 字段 基类 """
    creation_counter = 0

    
    def __init__(self, **arg):
        self.creation_order = FieldBase.creation_counter
        FieldBase.creation_counter+=1

        self._value      = None 
        self._attr       = arg.pop('attr' , {}) 
        self._validators = arg.pop('validators' , [])
        self._filters    = arg.pop('filters' , [])
        self._data       = arg.pop('data', [])
        self._type       = 'text'
        self._args       = arg
        self._on         = {
            # 验证错误时, 回调
            'error' : self.__class__.on_error
        }
        self._error      = None
        self._form       = False
        
        self.set_value(arg.pop('value' , None))

    def init(self, name, form):
        self._name = name 
        self._label = self._args.pop('label' , name)

        self._form = form
        self.on('error', form._on['error'])
        
    @staticmethod
    def on_error(element , msg):
        self._error = (element , msg)

    @property
    def attr(self):
        return self._attr

    def add_validator(self,validtor):
        self._validators.append(validtor)
        return self

    def set_validators(self,validtors):
        self._validators = validtors
        return self

    def add_filter(self,filter_name):

        self._filters.append(filter_name)
        return self

    # 返回 label
    def label(self):
        return self._label

    # 事件绑定
    def on(self,event,callback):
        self._on[event] = callback

    # 设置值
    def set_value(self,value):
        if None == value : return ''

        
        if Validators.is_array(value) and len(value) == 1:
            value = value[0]

        if Validators.is_number(value):
            value = int(value)

        if len(self._data) == 0:
            #过滤
            for v in self._filters:
                if hasattr(Filters , v):
                    value = getattr(Filters , v)(value)      
            self._value = value
            return 

        for v in self._data :
            if str(v['value']) == str(value) :
                self._value = v['value']
                return


    # 取值
    def get_value(self):
        return self._value

    # 取配置
    def get_config(self):
        validators = []
        for v in self._validators:
            cfg = v.get_config()
            cfg['message'] = self._form._(cfg['message'])
            validators.append(cfg)

        value = self.get_value()
        if 'to_json' in self._filters \
        and ( Validators.is_array(value) or Validators.is_dict(value) ):
            value = Json.encode(value)

        return {
            'name'       : self._name ,
            'label'      : self._form._(self._label) ,
            'value'      : value ,
            'attr'       : self._attr ,
            'validators' : validators ,
            'filters'    : self._filters ,
            'data'       : self._data ,
            'type'       : self._type 
        }

    # 验证数据
    def validate(self):
        value = self.get_value()

        for v in self._validators:
            if False == v.validator(self._form , self): 
                return False
        return True

class Button(FieldBase):
    
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'button'

    def set_value(self,value):
        self._value = value

    def validate(self):
        return True
        
class Submit(FieldBase):
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'submit'

    def set_value(self,value):
        self._value = value

    def validate(self):
        return True

class Hidden(FieldBase):
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'hidden'
        
class Password(FieldBase):
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'password'
        

class Text(FieldBase):
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'text'

class Select(FieldBase):
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'select'
        
class Radio(FieldBase):
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'radio'

class Textarea(FieldBase):
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'textarea'

class Checkbox(FieldBase):
    def __init__(self, **arg):
        FieldBase.__init__(self, **arg)
        self._type = 'checkbox'
        self._value = []
        if 'to_json' in self._filters:
            self._value = '[]'

    # 设置值
    def set_value(self,value):
        if Validators.is_empty(value):
            if 'to_json' in self._filters:
                self._value = '[]'
            return
         
        if False == Validators.is_array(value) \
        and 'to_json' in self._filters:
            value = Json.decode(value)    

        if False == Validators.is_array(value) :
            value = [value]
        self._value = []
        for v in self._data :
            for v1 in value: 
                if str(v['value']) == str(v1) :
                    self._value.append(v['value'])

        if 'to_json' in self._filters:
            self._value = Json.encode(self._value)




class Meta(type):
    def __new__(meta, classname, bases, classDict):
        cls = super(Meta, meta).__new__(meta, classname, bases, classDict)
        cls._meta = sorted(inspect.getmembers(cls,lambda o:isinstance(o,FieldBase)),key=lambda i:i[1].creation_order) 

        return cls

class Form(with_metaclass(Meta)):
    
    def __init__(self, translate=False, handler=False, action="" , method="POST" , enctype="multipart/form-data" , attr={}):
        self.action    = action
        self.method    = method
        self.enctype   = enctype
        self.attr      = attr
        self._values   = {}
        self._on       = {
            # 验证错误时, 回调
            'error' : self.on_error
        }
        self._handler = handler
        # 多语言支持
        self._        = self.translate()
        self._error   = False
        self._fields  = []
        for name, field in self._meta:
            field.init(name, self)
         
            self._fields.append(field)

    def translate(self):
        if self._handler and hasattr(self._handler, '_'):
            return self._handler._
        def _(string):
            return string
        return _

    @staticmethod
    def on_error(field, msg):
        field._form._error = (field, msg)

    @property
    def error_msg(self):
        return self._error

    def field(self, name):
        for v in self._fields:
            if v._name == name:
                return v
        return False

    # 事件绑定
    def on(self,event,callback):
        self._on[event] = callback
        for f in self._fields:
            f.on(event,callback)

    # 添加过滤
    def add_filter(self,name,callback):
        setattr(filters , name , callback)

    

    def get_config(self):
        config = {
            'action'   : self.action ,
            'method'   : self.method ,
            'enctype'  : self.enctype ,
            'attr'     : self.attr ,
            'fields' : [] ,
        }
        for e in self._fields:
            config['fields'].append(e.get_config())

        return config

    # 取验证过后的数据
    def values(self):
        return self._values

    # 设置表单值
    def set_values(self,data):
        
        for e in self._fields:
            if data.has_key(e._name):
                e.set_value(data[e._name])
            elif Validators.is_number(e._name) \
              and data.has_key(int(e._name)):
                e.set_value(data[int(e._name)])

    # 取表单默认值(注:值未经过验证)
    def get_default_values(self):
        values = {}
        for e in self._fields: 
            values[e._name] = e.get_value()
        return values

    def send_error(self):
        if self._handler:
            e , msg = self.error_msg
            return self._handler.write_error(
                msg = self._handler._('%s : %s' % ( e.label() , msg ) )
            ) 
        return False

    # 验证数据
    def validate(self,data = None):
        if not data and self._handler:
            data = self._handler.request.arguments

        _data = {}
        for k in data:
            _data[ k.replace('[]' , '') ] = data[k]

        for e in self._fields:       
            if _data.has_key(e._name):
                e.set_value(_data[e._name])
            elif Validators.is_number(e._name) \
            and _data.has_key(int(e._name)):
                e.set_value(_data[int(e._name)])

            if e.validate():
                if e._type != 'submit' and e._type != 'button':
                    self._values[e._name] = e.get_value()
            else:
                return False

        return self.values()

if __name__ == '__main__':
    
    class TestForm(Form):
        name = Text()
        sex = Select(
            data = [
                {'label': 'test', 'value': 24}
            ]
        )
    
    f = TestForm() 
    print f.get_config()
    