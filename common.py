#!/usr/bin/env python

import os
import re

build_path = ''
src_path = ''

## Map the message type to its message id range.
mtype2range = {
    'Syntax_Errors' : (1, 200),
    'Internal_Errors' : (200, 300),
    'Fatal_Errors' : (300, 400),
    'Warnings' : (400, 700),
    'Informational' : (700, 900),
    'Elective_Notes' : (900, 1000)
    }

fileTypes = ['c', 'h']

## Common pattern for message specified by lint.
## Like [PC-Lint 960]
lint_msg_pat = r'\[PC-Lint [\d]{1,3}\]'

def toInt(s):
    m = re.search(r'[\d]{1,4}', s) 
    return int(m.group(0))

def getMsgTypes():
    return mtype2range.keys()

def getMsgTypeByID(msgid):
    """
    Return string format of message type of a given
    message id 'msgid'.
    """
    for mtype, rg in mtype2range.iteritems():
        if msgid in range(rg[0], rg[1]):
            return mtype

def getRangeOfMsgType(mtype):
    return mtype2range[mtype]
        
