#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import validator
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
def parse_meta(filename, data):
    if "." not in filename:
        raise MetaParsingException(
            "Can't recognize type of your metadata ('%s')!" % filename
        )

    suffix = filename.rsplit(".", 1)[1].lower()

    if suffix not in SUPPORTED_FILES:
        raise MetaParsingException("Can't parse file of type '%s'!" % suffix)

    fp = validator.FieldParser()
    for key, val in SUPPORTED_FILES[suffix](data).items():
        fp.process(key, val)

    return fp.get_epublication()
