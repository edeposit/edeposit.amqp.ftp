#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import fields

import parser_csv
import parser_xml
import parser_yaml
import parser_json

from meta_exceptions import MetaParsingException


#= Variables ==================================================================
SUPPORTED_FILES = {
    "csv": parser_csv.decode,
    "json": parser_json.decode,
    "xml": parser_xml.decode,
    "yaml": parser_yaml.decode
}


#= Functions & objects ========================================================
def parse_meta(fn, data):
    if "." not in fn:
        raise MetaParsingException(
            "Can't recognize type of your metadata ('%s')!" % fn
        )

    suffix = fn.rsplit(".", 1)[1].lower()

    if suffix not in SUPPORTED_FILES:
        raise MetaParsingException("Can't parse file of type '%s'!" % suffix)

    parser = fields.FieldParser()
    for key, val in SUPPORTED_FILES[suffix](data).items():
        parser.process(key, val)

    return parser.get_epublication()
