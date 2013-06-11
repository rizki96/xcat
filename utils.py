#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-05-27 16:49:28
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

__all__ = [
    'md5',
    'Json',
    'Date',
    'Filters',
    'Validators',
]


import types
import re
import time
import hashlib
import sys
from HTMLParser import HTMLParser
from tornado import escape


def md5(s):
    m = hashlib.md5(str(s))
    m.digest()
    return m.hexdigest()

class Json:
    
    @staticmethod
    def decode(s,default=[]):
        s = Filters.trim(str(s))
        if '' == s:
            return default
        try:
            return escape.json_decode(s)
        except Exception, e:
            return default


    @staticmethod
    def encode(json):
        return escape.json_encode(json)
   


class Filters:

    """
    过滤字符 
    =============

    #### 方法:

     - trim 去除两边空格
     - to_number 转换成数字
     - to_text 转换成纯文本
     #- to_json 转换成json

    """

    @staticmethod
    def trim(s):
        return str(s).strip()

    @staticmethod
    def to_number(s):
        if Validators.is_number(s):
            return int(s)
        if Validators.is_float(s):
            return float(s)
        return 0

    @staticmethod
    def to_time(x):
        arr = str(x).split(':')
        if len(arr) == 2:
            # 小时
            hour = int(arr[0])
            # 分钟
            minute = int(arr[1])
            if 0 > hour or hour > 23:
                return '00:00'

            if 1 > minute or minute > 59:
                return '00:00'

            hour = str(hour)
            if int(hour) < 10:
                hour = '0' + hour
          
            minute = str(minute)
            if int(minute) < 10:
                minute = '0' + minute
            
            return '%s:%s' % (hour, minute)
                
        return '00:00' 

    # @staticmethod
    # def to_json(s):
    #     return Json.encode(s)

   
    @staticmethod
    def to_text(s):
        if None == s : return None
        html   = s.strip()
        html   = html.strip("\n")
        result = []
        parser = HTMLParser()
        parser.handle_data = result.append
        parser.feed(html)
        parser.close()
        return ''.join(result)




class Validators:
    '''
    验证类
    =============

    #### 方法:

     - is_string 是否字符
     - is_number 是否数字
     - is_float 是否浮点数
     - is_dict 是否字典
     - is_array 是否数组
     - is_empty 是否为空(含None)
     - is_date 是否符合日历规则 2010-01-31
     - is_email 是否邮件地址
     - is_chinese_char_string 是否为中文字符串
     - is_legal_accounts 是否合法 字母开头，允许4-16字节，允许字母数字下划线
     - is_ip_addr 是否ip地址

    '''

    @staticmethod
    def is_string(x):
        return type(x) is types.StringType

    @staticmethod
    def is_number(x):
        rule = '[+-]?\d+$'
        return re.match(rule, str(x))
            
    #判断是否为浮点数 1.324
    @staticmethod
    def is_float(x):
        return type(x) is types.FloatType

    #判断是否为字典 {'a1':'1','a2':'2'}
    @staticmethod
    def is_dict(x):
        return type(x) is types.DictType

    @staticmethod
    def is_array(x):
        return type(x) is types.ListType

    @staticmethod
    def is_empty(x):
        if type(x) is types.NoneType:
            return True
        if Validators.is_number(x): 
            return False
        return len(x) == 0

    #判断是否为日期格式,并且是否符合日历规则 2010-01-31
    @staticmethod
    def is_date(x):
        x = str(x)
        if len(x) == 10:
            rule = '(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)$/'
            match = re.match( rule , x )
            if match:
                return True
            return False
        return False



    #判断是否为邮件地址
    @staticmethod
    def is_email(x):
        x = str(x)
        rule = '[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'
        match = re.match( rule , x )

        if match:
            return True
        return False

    #判断是否为中文字符串
    @staticmethod
    def is_chinese_char_string(x):
        x = str(x)
        for v in x:
            if (v >= u"\u4e00" and v<=u"\u9fa5") or (v >= u'\u0041' and v<=u'\u005a') or (v >= u'\u0061' and v<=u'\u007a'):
                continue
            else:
                return False
        return True

    #判断帐号是否合法 字母开头，允许4-16字节，允许字母数字下划线
    @staticmethod
    def is_legal_accounts(x):
        x = str(x)
        rule = '[a-zA-Z][a-zA-Z0-9_]{3,15}$'
        match = re.match( rule , x )

        if match:
            return True
        return False

    #匹配IP地址
    @staticmethod
    def is_ip_addr(x):
        x = str(x)
        #rule = '\d+\.\d+\.\d+\.\d+'
        rule = '((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)'
        match = re.match( rule , x )

        if match:
            return True
        return False

