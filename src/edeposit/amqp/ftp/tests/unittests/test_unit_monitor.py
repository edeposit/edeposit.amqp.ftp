#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import pytest

import edeposit.amqp.ftp.monitor as monitor


#= Variables ==================================================================
#= Functions & objects ========================================================
def test_parse_line():
    l = monitor._parse_line("/path/to/the/he,ll, pcxaioay, EXIT, 1400508413")

    assert l["timestamp"] == "1400508413"
    assert l["command"] == "EXIT"
    assert l["username"] == "pcxaioay"
    assert l["path"] == "/path/to/the/he,ll"

    with pytest.raises(ValueError):
        monitor._parse_line("/path/to/the/hell, EXIT, 1400508413")
