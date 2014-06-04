#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module contains all communication structures used in AMQP communication.
"""
# Imports =====================================================================
from collections import namedtuple

import decoders
import settings


# Requests ====================================================================
class AddUser(namedtuple("AddUser", ["username", "password"])):
    """
    Add new user to the ProFTPD server.

    Args:
        username (str): Alloed characters: ``a-zA-Z0-9._-``.
        password (str): Password for the new user. Only hash is stored.
    """
    pass


class RemoveUser(namedtuple("RemoveUser", ["username"])):
    """
    Remove user from the ProFTPD server.

    Args:
        username (str): Alloed characters: ``a-zA-Z0-9._-``.
    """
    pass


class ChangePassword(namedtuple("ChangePassword", ["username",
                                                   "new_password"])):
    """
    Change password for the user.

    Args:
        username (str): Alloed characters: ``a-zA-Z0-9._-``.
        new_password (str): New password for user.

    """
    pass


class ListRegisteredUsers(namedtuple("ListRegisteredUsers", [])):
    """
    List all registered users.

    See also:
        :class:`Userlist`.
    """
    pass


class SetUserSettings(namedtuple("SetUserSettings",
                                 ["username"] + settings._ALLOWED_MERGES)):
    """
    Set settings for the user. :class:`UserSettings` is returned as response.

    See also:
        :class:`UserSettings`.
    """
    pass


class GetUserSettings(namedtuple("GetUserSettings", ["username"])):
    """
    Get settings for given `username`.

    :class:`UserSettings` is returned as response.

    See also:
        :class:`UserSettings`.
    """
    pass


# Responses ===================================================================
class Userlist(namedtuple("Userlist", ["users"])):
    """
    Response containing names of all users.

    Attributes:
        users (list): List of registered users.
    """
    pass


class UserSettings(namedtuple("UserSettings",
                              ["username"] + settings._ALLOWED_MERGES)):
    """
    All user settings, that user can set himself.
    """
    pass


class ImportRequest(namedtuple("ImportRequest",
                               ["username",
                                "requests",
                                "import_log",
                                "error_log"])):
    """
    User's import request - mix of files, metadata and metadata-files pairs.

    This request is sent asynchronously when user triggers the upload request.

    Attributes:
        username (str): Name of the user who sent an import request.
        requests (list): List of :class:`MetadataFile`/:class:`EbookFile`/
                         :class:`DataPair` objects.
        import_log (str): Protocol about import.
        error_log (str): Protocol about errors.
    """
    pass


# File structures =============================================================
class MetadataFile(namedtuple("MetadataFile", ["filename",
                                               "raw_data",
                                               "parsed_data"])):
    """
    Structure used to represent Metadata files.

    Attributes:
        filename (str): Name of the parsed file.
        raw_data (str): Content of the parsed file.
        parsed_data (EPublication): :class:`EPublication
                <edeposit.amqp.aleph.datastructures.epublication.EPublication>`
                structure.
    """
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

    def _parse(self):
        """
        Parse :attr:`raw_data`.

        Returns:
            MetadataFile: New MetadataFile with parsed data inside (namedtuples
                          are immutable).
        """
        return MetadataFile(
            self.filename,
            self.raw_data,
            decoders.parse_meta(self.filename, self.raw_data)
        )

    def _get_filenames(self):
        """
        Returns:
            list: of filenames (usually list with one filename).
        """
        return [self.filename]


class EbookFile(namedtuple("EbookFile", ["filename", "raw_data"])):
    """
    Structure used to represent data (ebook) files.

    Attributes:
        filename (str): Path to the ebook file.
        raw_data (str): Content of the file.
    """
    def __new__(self, filename, raw_data=None):
        if not raw_data:
            with open(filename) as f:
                raw_data = f.read()

        return super(EbookFile, self).__new__(self, filename, raw_data)

    def _get_filenames(self):
        """
        Returns:
            list: of filenames (usually list with one filename).
        """
        return [self.filename]


class DataPair(namedtuple("DataPair", ["metadata_file", "ebook_file"])):
    """
    Structure used to repesent MetadataFile - EbookFile pairs.

    Attributes:
        metadata_file (MetadataFile): Metadata.
        ebook_file (EbookFile): Data.
    """
    def _parse(self):
        """
        Parse metadata file inside.

        Returns:
            DataPair: New data pair (namedtuples are immutable).
        """
        return DataPair(self.metadata_file._parse(), self.ebook_file)

    def _get_filenames(self):
        """
        Returns:
            list: of filenames from objects in this container.
        """
        return [
            self.metadata_file.filename,  # don't change the order - used in RP
            self.ebook_file.filename
        ]
