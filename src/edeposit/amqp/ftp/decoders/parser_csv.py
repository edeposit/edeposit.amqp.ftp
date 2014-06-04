#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This submodule is used to parse metadata from CSV_ (``.csv``) files.

.. _CSV: https://en.wikipedia.org/wiki/Comma-separated_values

Example of the valid data::

    ISBN knihy;978-80-87270-99-8
    Vazba knihy;brož.
    Nazev knihy;whatever.csv
    Misto vydani;Praha
    Nakladatel;Garda
    Datum vydani;IX.12
    Poradi vydani;1
    Zpracovatel zaznamu;Franta Putsalek

See :doc:`/workflow/required` for list of required fields.
"""
#= Imports ====================================================================
import csv

import validator
from meta_exceptions import MetaParsingException


#= Functions & objects ========================================================
def _remove_quotes(word):
    """
    Remove quotes from `word` if the word starts and ands with quotes (" or ').
    """
    if not word or len(word) <= 2:
        return word

    if word[0] == word[-1] and word[0] in ["'", '"']:
        return word[1:-1]

    return word


def decode(data):
    """
    Handles decoding of the CSV `data`.

    Args:
        data (str): Data which will be decoded.

    Returns:
        dict: Dictionary with decoded data.
    """
    # try to guess dialect of the csv file
    dialect = None
    try:
        dialect = csv.Sniffer().sniff(data)
    except Exception:
        pass

    # parse data with csv parser
    handler = None
    try:
        data = data.splitlines()  # used later
        handler = csv.reader(data, dialect)
    except Exception, e:
        raise MetaParsingException("Can't parse your CSV data: %s" % e.message)

    # make sure, that data are meaningful
    decoded = []
    for cnt, line in enumerate(handler):
        usable_data = filter(lambda x: x.strip(), line)

        if not usable_data:
            continue

        if len(usable_data) != 2:
            raise MetaParsingException(
                "Bad number of elements - line %d:\n\t%s\n" % (cnt, data[cnt])
            )

        # remove trailing spaces, decode to utf-8
        usable_data = map(lambda x: x.strip().decode("utf-8"), usable_data)

        # remove quotes if the csv.Sniffer failed to decode right `dialect`
        usable_data = map(lambda x: _remove_quotes(x), usable_data)

        decoded.append(usable_data)

    # apply another checks to data
    decoded = validator.check_structure(decoded)

    return decoded
