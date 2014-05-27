#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import edeposit.amqp.ftp.decoders as decoders


# Variables ===================================================================
JSON_TEST_DATA = """
[
    "ISBN knihy", "80-86056-31-7",
    "Vazba knihy", "brož.",
    "Název knihy", "ZEN",
    "Místo vydáni", "Praha",
    "Nakladatel", "Garda",
    "Datum vydani", "09/2012",
    "Poradi vydani", "1",
    "Zpracovatel zaznamu", "Franta Putsalek"
]
"""


# Tests =======================================================================
def test_parse_meta():
    with pytest.raises(decoders.MetaParsingException):
        decoders.parse_meta("asd", JSON_TEST_DATA)

    decoders.parse_meta("asd.json", JSON_TEST_DATA)

    r = decoders.parse_meta("/home/xex/asd.jSon", JSON_TEST_DATA)

    assert r.__class__.__name__ == "EPublication", "Bad type of structure."
    assert r.ISBN == "80-86056-31-7", "Badly resolved ISBN."
    assert r.mistoVydani == "Praha"

    with pytest.raises(decoders.MetaParsingException):
        decoders.parse_meta("asd.csv", JSON_TEST_DATA)
