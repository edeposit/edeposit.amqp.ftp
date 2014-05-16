#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import json

import parser
from meta_exceptions import MetaParsingException


#= Functions & objects ========================================================
def decode(data):
    decoded = None
    try:
        decoded = json.loads(data)
    except Exception, e:
        raise MetaParsingException("Can't parse your JSON data: %s" % e.message)

    decoded = parser.check_structure(decoded)

    return decoded
