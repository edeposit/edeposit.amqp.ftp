#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import edeposit.amqp.ftp.decoders as decoders
from edeposit.amqp.ftp.decoders import parser_csv

import pytest


#= Tests ======================================================================
def test_csv():
    def test_assertions(test_str):
        data = parser_csv.decode(test_str)
        assert data["isbn"] == "80-86056-31-7"
        assert data["vazba"] == u"pevná"

    # double quoted
    test_assertions(
        """
        "isbn", "80-86056-31-7"
        "vazba", "pevná"
        """
    )

    # single quoted
    test_assertions(
        """
        'isbn', '80-86056-31-7'
        'vazba', 'pevná'
        """
    )

    # unquoted
    test_assertions(
        """
        isbn, 80-86056-31-7
        vazba, pevná
        """
    )

    # mixed quotes
    test_assertions(
        """
        'isbn', '80-86056-31-7'
        "vazba", "pevná"
        """
    )

    with pytest.raises(decoders.MetaParsingException):
        parser_csv.decode('"isbn", "80-86056-31-7", "asd"')

    with pytest.raises(decoders.MetaParsingException):
        parser_csv.decode('"isbn", ')

    with pytest.raises(decoders.MetaParsingException):
        parser_csv.decode('"isbn"')
