#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This submodule is used to parse metadata from ``.json`` files.

Metadata can be stored either in dictionary or in flat array.

Example structure::

    {
        "ISBN knihy": "80-86056-31-7",
        "Vazba knihy": "brož.",
        "Nazev knihy": "80-86056-31-7.json",
        "Misto vydani": "Praha",
        "Nakladatel": "Garda",
        "Datum vydani": "09/2012",
        "Poradi vydani": "1",
        "Zpracovatel zaznamu": "Franta Putsalek"
    }

or::

    [
        "ISBN knihy", "80-86056-31-7",
        "Vazba knihy", "brož.",
        "Nazev knihy", "samename.json",
        "Misto vydani", "Praha",
        "Nakladatel", "Garda",
        "Datum vydani", "09/2012",
        "Poradi vydani", "1",
        "Zpracovatel zaznamu", "Franta Putsalek"
    ]

See :doc:`/api/required` for list of required fields.
"""
#= Imports ====================================================================
import json

import parser
from meta_exceptions import MetaParsingException


#= Functions & objects ========================================================
def decode(data):
    """Handles decoding of the JSON `data`."""
    decoded = None
    try:
        decoded = json.loads(data)
    except Exception, e:
        raise MetaParsingException("Can't parse your JSON data: %s" % e.message)

    decoded = parser.check_structure(decoded)

    return decoded
