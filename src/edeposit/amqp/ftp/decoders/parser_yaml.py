#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This submodule is used to parse metadata from YAML_ (``.yaml``) files.

.. _YAML: https://en.wikipedia.org/wiki/YAML

Example of the valid data::

    ISBN knihy: 80-86056-31-7
    Vazba knihy: brož.
    Nazev knihy: 80-86056-31-7.json
    Misto vydani: Praha
    Nakladatel: Garda
    Datum vydani: 09/2012
    Poradi vydani: 1
    Zpracovatel zaznamu: Franta Putsalek

See :doc:`/workflow/required` for list of required fields.
"""
#= Imports ====================================================================
import yaml

import validator
from meta_exceptions import MetaParsingException


#= Functions & objects ========================================================
def decode(data):
    """
    Handles decoding of the YAML `data`.

    Args:
        data (str): Data which will be decoded.

    Returns:
        dict: Dictionary with decoded data.
    """
    decoded = None
    try:
        decoded = yaml.load(data)
    except Exception, e:
        e = e.message if e.message else str(e)
        raise MetaParsingException("Can't parse your YAML data: %s" % e)

    decoded = validator.check_structure(decoded)

    return decoded
