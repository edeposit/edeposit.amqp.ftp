#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This submodule is used to parse metadata from XML_ (``.xml``) files.

.. _XML: https://en.wikipedia.org/wiki/XML

Format schema::

    <root>
        <item key="key">value</item>
    </root>


Example of valid data::

    <root>
        <item key="ISBN knihy">80-86056-31-7</item>
        <item key="Vazba knihy">brož.</item>
        <item key="Nazev knihy">standalone2.xml</item>
        <item key="Misto vydani">Praha</item>
        <item key="Nakladatel">Garda</item>
        <item key="Datum vydani">09/2012</item>
        <item key="Poradi vydani">1</item>
        <item key="Zpracovatel zaznamu">Franta Putsalek</item>
    </root>

See :doc:`/workflow/required` for list of required fields.
"""
#= Imports ====================================================================
import dhtmlparser

import validator
from meta_exceptions import MetaParsingException


#= Functions & objects ========================================================
def decode(data):
    """
    Handles decoding of the XML `data`.

    Args:
        data (str): Data which will be decoded.

    Returns:
        dict: Dictionary with decoded data.
    """
    dom = None
    try:
        dom = dhtmlparser.parseString(data)
    except Exception, e:
        raise MetaParsingException("Can't parse your XML data: %s" % e.message)

    root = dom.find("root")

    # check whether there is <root>s
    if not root:
        raise MetaParsingException("All elements have to be inside <root>.")

    # and make sure, that there is not too many <root>s
    if len(root) > 1:
        raise MetaParsingException("Too many <root> elements in your XML!")

    items = root[0].find("item")

    # check for items
    if not items:
        raise MetaParsingException("There are no <items> in your XML <root>!")

    decoded = []
    for item in items:
        if "key" not in item.params:
            raise MetaParsingException(
                "There is no 'key' parameter in %s." % str(item)
            )

        decoded.append([
            item.params["key"],
            item.getContent().strip()
        ])

    decoded = validator.check_structure(decoded)

    return decoded
