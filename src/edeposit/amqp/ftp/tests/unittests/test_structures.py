#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import edeposit.amqp.ftp.decoders as decoders
import edeposit.amqp.ftp.structures as structures


# Variables ===================================================================
JSON_DATA = """
[
    "ISBN knihy", "80-86056-31-7",
    "Vazba knihy", "brož.",
    "Nazev knihy", "ZEN",
    "Misto vydani", "Praha",
    "Nakladatel", "Garda",
    "Datum vydani", "09/2012",
    "Poradi vydani", "1",
    "Zpracovatel zaznamu", "Franta Putsalek"
]
"""


# Functions & objects =========================================================
def test_parse_MetadataFile():
    mf = structures.MetadataFile("filename.json", JSON_DATA)

    assert mf.filename == "filename.json"
    assert mf.raw_data == JSON_DATA
    assert mf.parsed_data is None
    assert mf._get_filenames() == ["filename.json"]

    mf = mf._parse()

    assert mf.parsed_data.ISBN == "80-86056-31-7"

    mf = structures.MetadataFile("filename.csv", JSON_DATA)
    with pytest.raises(decoders.MetaParsingException):
        mf._parse()


def test_parse_EbookFile():
    ef = structures.EbookFile("asd.data", "some_data")

    assert ef.filename == "asd.data"
    assert ef.raw_data == "some_data"
    assert ef._get_filenames() == ["asd.data"]


def test_parse_DataPair():
    dp = structures.DataPair(
        structures.MetadataFile("filename.json", JSON_DATA),
        structures.EbookFile("asd.data", "some_data")
    )

    # test ._get_filenames()
    assert len(dp._get_filenames()) == 2
    assert "filename.json" in dp._get_filenames()
    assert "asd.data" in dp._get_filenames()

    assert dp.metadata_file.filename == "filename.json"
    assert dp.ebook_file.filename == "asd.data"

    assert dp.metadata_file.parsed_data is None

    dp = dp._parse()

    assert dp
    assert dp.metadata_file.filename == "filename.json"
    assert dp.metadata_file.parsed_data.ISBN == "80-86056-31-7"
    assert dp.ebook_file.filename == "asd.data"
