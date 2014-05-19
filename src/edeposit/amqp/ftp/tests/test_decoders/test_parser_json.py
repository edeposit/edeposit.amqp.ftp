#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import edeposit.amqp.ftp.decoders as decoders
from edeposit.amqp.ftp.decoders import parser_json


#= Tests ======================================================================
def test_json():
    def test_assertions(test_str):
        data = parser_json.decode(test_str)
        assert data["isbn"] == "80-86056-31-7"
        assert data["vazba"] == u"pevná"

    # dict
    test_str = """
    {
        "isbn": "80-86056-31-7",
        "vazba": "pevná"
    }
    """
    test_assertions(test_str)

    # array
    test_str = """
    [
        "isbn", "80-86056-31-7",
        "vazba", "pevná"
    ]
    """
    test_assertions(test_str)

    try:
        parser_json.decode('[["isbn"], "80-86056-31-7", "asd"]')
        raise AssertionError("Field check failed!")
    except decoders.MetaParsingException:
        pass
