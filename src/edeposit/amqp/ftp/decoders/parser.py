#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module provides highlevel checking of parsed data for lowlevel decoders.

It handles the unicode in keys, builds dicts from flat arrays and so on.
"""
# Imports =====================================================================
import unicodedata

try:
    from aleph.isbn import is_valid_isbn
    from aleph.datastructures.epublication import EPublication
except ImportError:
    from edeposit.amqp.aleph.isbn import is_valid_isbn
    from edeposit.amqp.aleph.datastructures.epublication import EPublication

from meta_exceptions import MetaParsingException


# Variables ===================================================================
_ALLOWED_TYPES = [
    str,
    unicode,
    int,
    float,
    long
]

_ITERABLE_TYPES = [
    list,
    tuple
]


# Functions & objects =========================================================
class Field:
    """
    This class is used to represent and parse specific "key: val" pair.

    When you create the object, `keyword` and `descr` is specified. Optionally
    also `epub` parameter, which is corresponding key in :class:`EPublication
    <edeposit.amqp.aleph.datastructures.epublication.EPublication>` structure.

    Assingning value to the class is done by calling :meth:`check`, which
    sets the :attr:`value`, if the `key` parameter matches :attr:`keyword`.

    Args:
        keyword (str): Key for the data pair.
        descr (str): Description of the data pair. Used in exceptions.
        epub (str, default None): Corresponding keyword in EPublication
                                  structure.
    """
    def __init__(self, keyword, descr, epub=None):
        #: Keyword agains :meth:`check` will try to match.
        self.keyword = keyword

        #: Description of the data pair.
        self.descr = descr

        #: Internal value. Set when :meth:`check` successfully matched the
        #: keyword.
        self.value = None

        #: Corresponding key in :class:`EPublication
        #: <edeposit.amqp.aleph.datastructures.epublication.EPublication>`
        #: structure.
        self.epub = epub if epub is not None else self.keyword

    def check(self, key, value):
        """
        Check whether `key` matchs the :attr:`keyword`. If so, set the
        :attr:`value` to `value`.

        Args:
            key (str): Key which will be matched with :attr:`keyword`.
            value (str): Value which will be assigned to :attr:`value` if keys
                         matches.

        Returns:
            True/False: Whether the key matched :attr:`keyword`.
        """
        key = key.lower().strip()

        # try unicode conversion
        try:
            key = key.decode("utf-8")
        except UnicodeEncodeError:
            pass

        key = self._remove_accents(key)

        if self.keyword in key.split():
            self.value = value
            return True

        return False

    def is_valid(self):
        """
        Return ``True`` if :attr:`value` is set.

        Note:
            :attr:`value` is set by calling :meth:`check` with proper `key`.
        """
        return self.value is not None

    def _remove_accents(self, input_str):
        """
        Convert unicode string to ASCII.

        Credit: http://stackoverflow.com/a/517974
        """
        nkfd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


class FieldParser:
    """
    Class used to make sure, that all fields in metadata are present.

    See :doc:`/api/required` for list of required fields.
    """
    def __init__(self):
        self.fields = [
            Field(keyword="isbn", descr="ISBN", epub="ISBN"),
            Field(keyword="vazba", descr="Vazba/forma"),
            Field(keyword="nazev", descr="Název"),
            Field(keyword="misto", descr="Místo vydání", epub="mistoVydani"),
            Field(
                keyword="nakladatel",
                descr="Nakladatel",
                epub="nakladatelVydavatel"
            ),
            Field(
                keyword="datum",
                descr="Měsíc a rok vydání",
                epub="datumVydani"
            ),
            Field(keyword="poradi", descr="Pořadí vydání", epub="poradiVydani"),
            Field(
                keyword="zpracovatel",
                descr="Zpracovatel záznamu",
                epub="zpracovatelZaznamu"
            )
        ]

        self.optional = [
            Field(keyword="url", descr="Url"),
            Field(keyword="format", descr="Formát"),
            Field(keyword="podnazev", descr="Podnázev"),
            Field(keyword="cena", descr="Cena"),
        ]

    def process(self, key, val):
        """
        Try to look for `key` in all required and optional fields. If found,
        set the `val`.
        """
        for field in self.fields:
            if field.check(key, val):
                return

        for field in self.optional:
            if field.check(key, val):
                return

    def is_valid(self):
        """
        Returns:
            True/False whether ALL required fields are set.
        """
        for field in self.fields:
            if not field.is_valid():
                return False

        return True

    def get_epublication(self):
        """
        Returns:
            EPublication: Structure when the object :meth:`is_valid`.

        Raises:
            MetaParsingException: When the object is not valid.
        """
        if not self.is_valid():
            bad_fields = filter(lambda x: not x.is_valid(), self.fields)
            bad_fields = map(
                lambda x: "Keyword '%s' (%s) not found." % (x.keyword, x.descr),
                bad_fields
            )

            raise MetaParsingException(
                "Missing field(s):\n\t" + "\n\t".join(bad_fields)
            )

        relevant_fields = self.fields
        relevant_fields += filter(lambda x: x.is_valid(), self.optional)

        epub_dict = dict(map(lambda x: (x.epub, x.value), relevant_fields))

        # make sure, that all fields present in EPublication has values also
        # in epub_dict
        for epublication_part in EPublication._fields:
            if epublication_part not in epub_dict:
                epub_dict[epublication_part] = None

        if not is_valid_isbn(epub_dict["ISBN"]):
            raise MetaParsingException(
                "ISBN '%s' is not valid!" % epub_dict["ISBN"]
            )

        return EPublication(**epub_dict)


def _all_correct_list(array):
    """
    Make sure, that all items in `array` has good type and size.

    Args:
        array (list): Array of python types.

    Returns:
        True/False
    """
    if type(array) not in _ITERABLE_TYPES:
        return False

    for item in array:
        if not type(item) in _ITERABLE_TYPES:
            return False

        if len(item) != 2:
            return False

    return True


def _convert_to_dict(data):
    """
    Convert `data` to dictionary.

    Tries to get sense in multidimensional arrays.

    Args:
        data: List/dict/tuple of variable dimension.

    Returns:
        dict: If the data can be converted to dictionary.

    Raises:
        MetaParsingException: When the data are unconvertible to dict.
    """
    if isinstance(data, dict):
        return data

    if isinstance(data, list) or isinstance(data, tuple):
        if _all_correct_list(data):
            return dict(data)
        else:
            data = zip(data[::2], data[1::2])
            return dict(data)
    else:
        raise MetaParsingException(
            "Can't decode provided metadata - unknown structure."
        )


def check_structure(data):
    """
    Check whether the structure is flat dictionary. If not, try to convert it
    to dictionary.

    Args:
        data: Whatever data you have (dict/tuple/list).

    Returns:
        dict: When the conversion was successful or `data` was already `good`.

    Raises:
        MetaParsingException: When the data couldn't be converted or had `bad`
                              structure.
    """
    if not isinstance(data, dict):
        try:
            data = _convert_to_dict(data)
        except MetaParsingException:
            raise
        except:
            raise MetaParsingException(
                "Metadata format has invalid strucure (dict is expected)."
            )

    for key, val in data.iteritems():
        if type(key) not in _ALLOWED_TYPES:
            raise MetaParsingException(
                "Can't decode the meta file - invalid type of keyword '" +
                str(key) +
                "'!"
            )
        if type(val) not in _ALLOWED_TYPES:
            raise MetaParsingException(
                "Can't decode the meta file - invalid type of keyword '" +
                str(key) +
                "'!"
            )

    return data
