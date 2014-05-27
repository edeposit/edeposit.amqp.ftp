#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
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
ALLOWED_TYPES = [
    str,
    unicode,
    int,
    float,
    long
]

ITERABLE_TYPES = [
    list,
    tuple
]


# Functions & objects =========================================================
class Field:
    def __init__(self, keyword, descr, epub=None):
        self.keyword = keyword
        self.descr = descr
        self.value = None
        self.epub = epub if epub is not None else self.keyword

    def check(self, key, value):
        key = key.lower().strip()

        # try unicode conversion
        try:
            key = key.decode("utf-8")
        except UnicodeEncodeError:
            pass

        key = self.remove_accents(key)

        if self.keyword in key.split():
            self.value = value
            return True

        return False

    def is_valid(self):
        """
        Return True if :attr:`self.value` is set.

        Note:
            Value is set by calling :method:`check` with proper `key`.
        """
        return self.value is not None

    def remove_accents(self, input_str):
        """
        Convert unicode string to ASCII.

        Credit: http://stackoverflow.com/a/517974
        """
        nkfd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


class FieldParser:
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
        for field in self.fields:
            if field.check(key, val):
                return

        for field in self.optional:
            if field.check(key, val):
                return

    def is_valid(self):
        for field in self.fields:
            if not field.is_valid():
                return False

        return True

    def get_epublication(self):
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

        for epublication_part in EPublication._fields:
            if epublication_part not in epub_dict:
                epub_dict[epublication_part] = None

        if not is_valid_isbn(epub_dict["ISBN"]):
            raise MetaParsingException(
                "ISBN '%s' is not valid!" % epub_dict["ISBN"]
            )

        return EPublication(**epub_dict)


def _all_correct_list(array):
    if type(array) not in ITERABLE_TYPES:
        return False

    for item in array:
        if not type(item) in ITERABLE_TYPES:
            return False

        if len(item) != 2:
            return False

    return True


def convert_to_dict(data):
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
    Check whether the structure is flat dictionary.
    """
    if not isinstance(data, dict):
        try:
            data = convert_to_dict(data)
        except MetaParsingException:
            raise
        except:
            raise MetaParsingException(
                "Metadata format has invalid strucure (dict is expected)."
            )

    for key, val in data.iteritems():
        if type(key) not in ALLOWED_TYPES:
            raise MetaParsingException(
                "Can't decode the meta file - invalid type of keyword '" +
                str(key) +
                "'!"
            )
        if type(val) not in ALLOWED_TYPES:
            raise MetaParsingException(
                "Can't decode the meta file - invalid type of keyword '" +
                str(key) +
                "'!"
            )

    return data
