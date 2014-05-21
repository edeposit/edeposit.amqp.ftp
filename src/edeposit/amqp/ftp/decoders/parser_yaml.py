#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import yaml

import parser
from meta_exceptions import MetaParsingException


#= Functions & objects ========================================================
def decode(data):
    decoded = None
    try:
        decoded = yaml.load(data)
    except Exception, e:
        e = e.message if e.message else str(e)
        raise MetaParsingException("Can't parse your YAML data: %s" % e)

    decoded = parser.check_structure(decoded)

    return decoded
