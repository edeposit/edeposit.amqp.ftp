#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
try:
    from aleph.datastructures.epublication import EPublication
except ImportError:
    from edeposit.amqp.aleph.datastructures.epublication import EPublication

from meta_exceptions import MetaParsingException


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

    def get_epublication(self):  # TODO: validaci isbn
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

        return EPublication(**epub_dict)


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
    from parser import assert_exc

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
