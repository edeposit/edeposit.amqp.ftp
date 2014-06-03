#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
"""
Exceptions for :mod:`.decoders` submodule.
"""


# Classes =====================================================================
class MetaParsingException(UserWarning):
    """
    Main exception used in every decoder.

    Note:
        You souldn't get anything else from the whole :mod:`.decoders`
        submodule.
    """
    def __init__(self, message):
        super(MetaParsingException, self).__init__(message)
