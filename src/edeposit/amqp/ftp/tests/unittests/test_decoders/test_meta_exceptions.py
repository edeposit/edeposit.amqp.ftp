#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import edeposit.amqp.ftp.decoders as decoders


#= Tests ======================================================================
def test_meta_parsing_exception():
    try:
        raise decoders.MetaParsingException("Message")
    except decoders.MetaParsingException, e:
        assert e.message == "Message"
