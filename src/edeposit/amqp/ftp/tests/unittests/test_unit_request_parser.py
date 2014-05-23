#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import edeposit.amqp.ftp.structures as structures
import edeposit.amqp.ftp.request_parser as request_parser


# Functions & objects =========================================================
def setup_module():
    class LoggerMock:
        def debug(*args, **kwargs):
            pass
        def info(*args, **kwargs):
            pass

    request_parser.logger = LoggerMock()


def test_just_name():
    assert request_parser._just_name("/home/bystrousak/xex.asd") == "xex"
    assert request_parser._just_name("/home/bystrousak/xex") == "xex"


def test_same_named():
    out = request_parser._same_named(
        "/hello/joe.mp3",
        [
            "/hi/",
            "/ola/how/are/you/joe.jpg",
            "/ola/how/are/you/xex.jpg"
        ]
    )

    assert out[0][0] == 1
    assert out[0][1] == "/ola/how/are/you/joe.jpg"


def test_is_meta():
    assert request_parser._is_meta("asd.json")
    assert request_parser._is_meta("asd.jSon")
    assert request_parser._is_meta("asd.csv")
    assert request_parser._is_meta("asd.xml")
    assert request_parser._is_meta("asd.yaml")

    assert request_parser._is_meta("/home/xex/asd.yaml")

    assert not request_parser._is_meta("/home/xex/asd.yaml.txt")
    assert not request_parser._is_meta("/home/xex/yaml.txt")
    assert not request_parser._is_meta("yaml.txt")
    assert not request_parser._is_meta("yaml.xex")
    assert not request_parser._is_meta("yaml.")
    assert not request_parser._is_meta("yaml")


def test_index():
    data = [1, 2, 3, 4, "a", "b", "c"]

    assert request_parser._index(data, 1) == 0
    assert request_parser._index(data, "a") == 4
    assert request_parser._index(data, "c") == 6
    assert request_parser._index(data, "x") == -1


def test_isbn_pairing():
    data = [
        structures.EbookFile("/home/xex/80-86056-31-7.epub", "Random content."),
        structures.MetadataFile(
            "/80-86056-31-7.xml",
            "Random content.",
            "Parsed"
        )
    ]

    pair = request_parser._isbn_pairing(data[:])
    assert pair
    assert isinstance(pair[0], structures.DataPair)
    assert pair[0].metadata_file == data[1]
    assert pair[0].ebook_file == data[0]

    data = [
        structures.EbookFile("samename.epub", "Random content."),
        structures.MetadataFile(
            "samename.xml",
            "Random content.",
            "Parsed"
        )
    ]

    pair = request_parser._isbn_pairing(data[:])
    assert len(pair) == 2

    assert not filter(lambda x: isinstance(x, structures.DataPair), pair)