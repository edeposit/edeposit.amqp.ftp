#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple

import decoders


#= Requests ===================================================================
class AddUser(namedtuple("AddUser", ["username", "password"])):
    pass


class RemoveUser(namedtuple("RemoveUser", ["username", "password"])):
    pass


class ChangePassword(namedtuple("ChangePassword", ["username",
                                                   "new_password"])):
    pass


class ListRegisteredUsers(namedtuple("ListRegisteredUsers", [])):
    pass


#= Responses ==================================================================
class ImportRequest(namedtuple("ImportRequest", ["username", "requests"])):
    pass  # TODO: rewrite to differentiate metadata/actual data


class MetadataFile(namedtuple("MetadataFile", ["filename",
                                               "raw_data",
                                               "parsed_data"])):
    pass


class EbookFile(namedtuple("EbookFile", ["filename", "raw_data"])):
    pass


class DataPair(namedtuple("DataPair", ["metadata_file", "ebook_file"])):
    pass


class SendEmail(namedtuple("SendEmail", ["username", "subject", "text"])):
    pass


#= Functions & objects ========================================================
def read_meta_file(fn):
    with open(fn) as f:
        data = f.read()
        return MetadataFile(
            filename=fn,
            raw_data=data,
            parsed_data=decoders.read_meta(data)
        )


def read_data_file(fn):
    with open(fn) as f:
        data = f.read()
        return EbookFile(filename=fn, raw_data=data)
