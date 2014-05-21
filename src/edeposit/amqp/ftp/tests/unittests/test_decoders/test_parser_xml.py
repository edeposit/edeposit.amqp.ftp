#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import edeposit.amqp.ftp.decoders as decoders
from edeposit.amqp.ftp.decoders import parser_xml

import pytest


#= Tests ======================================================================
def test_csv():
    def test_assertions(test_str):
        data = parser_xml.decode(test_str)
        assert data["isbn"] == "80-86056-31-7"
        assert data["vazba"] == "pevná"

    test_assertions(
        """
        <root>
        <item key="isbn">80-86056-31-7</item>
        <item key="vazba">pevná</item>
        </root>
        """
    )

    test_assertions(
        """
        <root>
            <item key="isbn">
                80-86056-31-7
            </item>
            <item key="vazba">
                pevná
            </item>
        </root>
        """
    )

    with pytest.raises(decoders.MetaParsingException):
        parser_xml.decode('<root></root>')

    with pytest.raises(decoders.MetaParsingException):
        parser_xml.decode('<root><item></item></root>')

    with pytest.raises(decoders.MetaParsingException):
        parser_xml.decode('<root>')

    with pytest.raises(decoders.MetaParsingException):
        parser_xml.decode('<root><item></root>')
