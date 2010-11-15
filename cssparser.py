# -*- coding: utf-8 -*-
""" 
A CSS parser using funcparserlib.
"""
import sys
from pprint import pformat

from funcparserlib.lexer import make_tokenizer

from funcparserlib.parser import (some, a, maybe, many, finished, skip,
    forward_decl, NoParseError)

def tokenize(s):
    'str -> Sequence(Token)'
    alias = { 
        'h':            r'[0-9a-f]',
        'nonascii':     r'[\200-\377]',
        'unicode':      r'\\(%(h)s){1,6}(\r\n|[ \t\r\n\f])?',
        'escape':       r'(%(unicode)s)|\\[^\r\n\f0-9a-f]',
        'nmstart':      r'[_a-z]|(%(nonascii)s)|(%(escape)s)',
        'nmchar':       r'[_a-z0-9-]|(%(nonascii)s)|(%(escape)s)',
        'string1':      r'\"([^\n\r\f\\"]|\\(%(nl)s)|(%(escape)s))*\"',
        'string2':      r"\'([^\n\r\f\\']|\\(%(nl)s)|(%(escape)s))*\'",
        'invalid1':     r'\"([^\n\r\f\\"]|\\(%(nl)s)|(%(escape)s))*',
        'invalid2':     r"\'([^\n\r\f\\']|\\(%(nl)s)|(%(escape)s))*",
    
        'comment':      r'\/\*[^*]*\*+([^/*][^*]*\*+)*\/',
        'ident':        r'-?(%(nmstart)s)(%(nmchar)s)*',
        'name':		    r'(%(nmchar)s)+',
        'hash':		    r'#(%(name)s)+',
        'num':          r'([0-9]*\.[0-9]+|[0-9]+)',
        'string':       r'(%(string1)s)|(%(string2)s)',
        'invalid':	    r'(%(invalid1)s)|(%(invalid2)s)',
        'url':          '([!#$%(unprintable)s&*-~]|(%(nonascii)s)|(%(escape)s))*',
        's':		    r'[ \t\r\n\f]+',
        'w':		    r'(%(s)s)?',
        'nl':		    r'\n|\r\n|\r|\f',
        'unprintable':  '%(unprintable)s',

        'important':    r'!((%(w)s)|(%(comment)s))*(IMPORTANT|important)',
        'em':           r'(%(num)s)em',
        'ex':           r'(%(num)s)ex',
        'length':       r'(%(num)s)(px|cm|mm|in|pt|pc)',
        'angle':        r'(%(num)s)(deg|rad|grad)',
        'time':         r'(%(num)s)(ms|s)',
        'freq':         r'(%(num)s)(hz|khz)',
        'dimension':    r'(%(num)s)(%(ident)s)',
        'percentage':   r'(%(num)s)%(unprintable)s',
        
        'uri':          r'url\((%(w)s)((%(string)s)|(%(url)s))(%(w)s)\)',

        'function':     r'(%(ident)s)\(',

    }
    
    def applyTillDead(name, alias):
        s, sold = alias[name], ''
            
        while s != sold:
            sold = s
            s = s % alias
        return s
    
    for k in alias.keys():
        alias[k] = applyTillDead(k, alias)
    
    for k in alias.keys():
        alias[k] = alias[k] % {'unprintable': '%'}

    for k in alias.keys():
        alias[k] = (alias[k],)

    specs = [
        #spaces
        ('S', alias['s']),
    
        #comments
        ('COMMENT', alias['comment']),
    
        # html comments
        ('CDO',  ('<!--' ,)),
        ('CDC',  ('-->' ,)),
    
        ('INCLUDES', ('~=',)),
        ('DISMATCH', ('!=',)),
    
    
        #string
        ('STRING', alias['string']),
        ('INVALID', alias['invalid']),
    
        ('HASH', alias['hash']),
    
        ('IMPORT_SYM', ("@import|@IMPORT",)),
        ('PAGE_SYM', ("@page|@PAGE",)),
        ('MEDIA_SYM', ("@media|@MEDIA",)),
        ('CHARSET_SYM', ("@charset ",)),
    
        ('IMPORTANT_SYM', alias['important']),
        
        
        ('EMS', alias['em']),
        ('EXS', alias['ex']),
        ('LENGTH', alias['length']),
        ('ANGLE', alias['angle']),
        ('TIME', alias['time']),
        ('FREQ', alias['freq']),
        ('DIMENSION', alias['dimension']),
        
        ('PERCENTAGE', alias['percentage']),
        
        ('URI', alias['uri']),
        
        ('NUMBER', alias['num']),
    
        ('FUNCTION', alias['function']), 
        
        ('IDENT', alias['ident']),
        
        ('CHAR', ('.',)), 
    
    ]
    useless = ['COMMENT' ]
    t = make_tokenizer(specs)
    return [x for x in t(s) if x.type not in useless] 

def parse(seq):
    'Sequence(Token) -> object'
    const = lambda x : lambda _: x
    tokval = lambda x: x.value
    toktype = lambda t: some(lambda x: x.type == t) >> tokval
    op = lambda s: a(Token('Op', s)) >> tokval
    #css_text = 
    #css = skip(finished)
    number = some(lambda tok: tok.type == 'NUMBER') >> tokval >> int

    return type(number.parse(seq))


def loads(s):
    'str -> object'
    return parse(tokenize(s))

def main():
    try:
        input = sys.stdin.read().decode('utf-8')
        tree = loads(input)
        print pformat(tree)
    except SyntaxError, e:
        msg = (u'syntax error: %s' % e).encode(ENCODING)
        print >> sys.stderr, msg
        sys.exit(1)

if __name__ == '__main__':
    main()
