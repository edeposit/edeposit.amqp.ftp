#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple

import decoders
import settings


# Requests ====================================================================
class AddUser(namedtuple("AddUser", ["username", "password"])):
    pass


class RemoveUser(namedtuple("RemoveUser", ["username"])):
    pass


class ChangePassword(namedtuple("ChangePassword", ["username",
                                                   "new_password"])):
    pass


class ListRegisteredUsers(namedtuple("ListRegisteredUsers", [])):
    pass


class SetUserSettings(namedtuple("SetUserSettings",
                                 ["username"] + settings._ALLOWED_MERGES)):
    pass


class GetUserSettings(namedtuple("GetUserSettings", ["username"])):
    pass


# Responses ===================================================================
class Userlist(namedtuple("Userlist", ["users"])):
    pass


class SendEmail(namedtuple("SendEmail", ["username", "subject", "text"])):
    pass


class UserSettings(namedtuple("UserSettings",
                              ["username"] + settings._ALLOWED_MERGES)):
    pass


class ImportRequest(namedtuple("ImportRequest", ["username", "requests"])):
    pass  # TODO: protocol


# File structures =============================================================
class MetadataFile(namedtuple("MetadataFile", ["filename",
                                               "raw_data",
                                               "parsed_data"])):
    def __new__(self, filename, raw_data=None, parsed_data=None):
        if not raw_data:
            with open(filename) as f:
                raw_data = f.read()

        return super(MetadataFile, self).__new__(
            self,
            filename,
            raw_data,
            parsed_data
        )

    def parse(self):
        return MetadataFile(
            self.filename,
            self.raw_data,
            decoders.parse_meta(self.filename, self.raw_data)
        )

    def get_filenames(self):
        return [self.filename]


class EbookFile(namedtuple("EbookFile", ["filename", "raw_data"])):
    def __new__(self, filename, raw_data=None):
        if not raw_data:
            with open(filename) as f:
                raw_data = f.read()

        return super(EbookFile, self).__new__(self, filename, raw_data)

    def get_filenames(self):
        return [self.filename]


class DataPair(namedtuple("DataPair", ["metadata_file", "ebook_file"])):
    def parse(self):
        return DataPair(self.metadata_file.parse(), self.ebook_file)

    def get_filenames(self):
        return [
            self.metadata_file.filename,  # don't change the order - used in RP
            self.ebook_file.filename
        ]
