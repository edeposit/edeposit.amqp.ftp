#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
try:
    from aleph.isbn import is_valid_isbn
    from aleph.datastructures.epublication import EPublication
except ImportError:
    from edeposit.amqp.aleph.isbn import is_valid_isbn
    from edeposit.amqp.aleph.datastructures.epublication import EPublication

from meta_exceptions import MetaParsingException


#= Variables ==================================================================
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


#= Functions & objects ========================================================
class Field:
    def __init__(self, keyword, descr, epub=None):
        self.keyword = keyword
        self.descr = descr
        self.value = None
        self.epub = epub if epub is not None else self.keyword

    def check(self, key, value):
        if self.keyword in key.lower().strip().split():  # TODO: remove unicode?
            self.value = value
            return True

        return False

    def is_valid(self):
        return self.value is not None


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
                "Metadata format has invalid strucure (dictionary is expected)."
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


def assert_exc(data, fn, exc=MetaParsingException):
    try:
        if data:
            fn(data)
        else:
            fn()
        raise AssertionError(
            "%s() fails to recognize bad data: %s" % (fn.__name__, str(data))
        )
    except exc:
        pass


def test__all_correct_list():
    assert _all_correct_list([])
    assert _all_correct_list([[1, 2], [1, 2], [1, 2]])
    assert not _all_correct_list(1)
    assert not _all_correct_list([[1], [1]])
    assert not _all_correct_list([1, [1, 2]])
    assert not _all_correct_list([[]])


def test_convert_to_dict():
    assert convert_to_dict([1, 2]) == {1: 2}
    assert convert_to_dict({1: 2}) == {1: 2}

    assert_exc([[1, 2], 2, 3], convert_to_dict, TypeError)
    assert_exc(bool, convert_to_dict)


def test_check_structure():
    assert check_structure([1, 2, 3, 4]) == {1: 2, 3: 4}
    assert check_structure({1: 2, 3: 4}) == {1: 2, 3: 4}

    assert_exc(bool, check_structure)
    assert_exc([1, 2, [3], 4], check_structure)
    assert_exc([1, 2, {}, 4], check_structure)
    assert_exc([1, 2, {}, {}], check_structure)
    assert_exc({True: {}, 3: 4}, check_structure)

def test_field():
    f = Field("isbn", "ISBN of the book", "ISBN")
    assert not f.is_valid()

    assert not f.check("ehlo", "xex")
    assert f.value is None
    assert not f.is_valid()

    assert f.check("ISBN knihy", "80-86056-31-7")
    assert f.value == "80-86056-31-7"
    assert f.is_valid()
    assert f.epub == "ISBN"


def test_field_parser():
    f = FieldParser()

    assert len(f.fields) > 0

    # is not valid and should fail to requests for validation
    assert not f.is_valid()
    assert_exc(None, f.get_epublication)

    # put data into FieldParser
    f.process("ISBN knihy", "80-86056-31-7")
    assert not f.is_valid()
    f.process("Vazba knihy", "brož.")
    assert not f.is_valid()
    f.process("Nazev knihy", "ZEN")
    assert not f.is_valid()
    f.process("Misto vydani", "Praha")
    assert not f.is_valid()
    f.process("Nakladatel", "Garda")
    assert not f.is_valid()
    f.process("Datum vydani", "09/2012")
    assert not f.is_valid()
    f.process("Poradi vydani", "1")
    assert not f.is_valid()
    f.process("Zpracovatel zaznamu", "Franta Putsalek")
    assert f.is_valid()  # !

    # test if the data are correctly parsed
    e = f.get_epublication()
    assert e.ISBN == "80-86056-31-7"
    assert e.vazba == "brož."
    assert e.nazev == "ZEN"
    assert e.mistoVydani == "Praha"
    assert e.nakladatelVydavatel == "Garda"
    assert e.datumVydani == "09/2012"
    assert e.poradiVydani == "1"
    assert e.zpracovatelZaznamu == "Franta Putsalek"

    f.process("ISBN knihy", "80-XXXXX-XX-0")
    assert f.is_valid()
    assert_exc(None, f.get_epublication)