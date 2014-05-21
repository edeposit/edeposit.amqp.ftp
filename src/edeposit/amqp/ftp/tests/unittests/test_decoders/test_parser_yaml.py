#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import edeposit.amqp.ftp.decoders as decoders
from edeposit.amqp.ftp.decoders import parser_yaml

import pytest


#= Tests ======================================================================
def test_yaml():
    def test_assertions(test_str):
        data = parser_yaml.decode(test_str)
        assert data["isbn"] == "80-86056-31-7"
        assert data["vazba"] == u"pevná"

    test_assertions(
        """
        isbn: 80-86056-31-7
        vazba: pevná
        """
    )

    test_assertions(
        """
        isbn:
            80-86056-31-7
        vazba:
            pevná
        """
    )

    # added quote test
    test_assertions(
        """
        isbn: "80-86056-31-7"
        vazba: "pevná"
        """
    )

    with pytest.raises(decoders.MetaParsingException):
        parser_yaml.decode('isbn: 80-86056-31-7: xex')

    with pytest.raises(decoders.MetaParsingException):
        parser_yaml.decode('isbn:')

    with pytest.raises(decoders.MetaParsingException):
        parser_yaml.decode('isbn')
