#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import pytest

import edeposit.amqp.ftp.monitor as monitor
import edeposit.amqp.ftp.request_parser as request_parser


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


def test_recursive_chmod():
    raise NotImplementedError()


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
