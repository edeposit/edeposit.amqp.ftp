#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import edeposit.amqp.ftp.decoders as decoders
from edeposit.amqp.ftp.decoders import parser


#= Functions & objects ========================================================
def assert_exc(data, fn, exc=decoders.MetaParsingException):
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


#= Tests ======================================================================
class TestParser:
    def test__all_correct_list(self):
        assert parser._all_correct_list([])
        assert parser._all_correct_list([[1, 2], [1, 2], [1, 2]])
        assert not parser._all_correct_list(1)
        assert not parser._all_correct_list([[1], [1]])
        assert not parser._all_correct_list([1, [1, 2]])
        assert not parser._all_correct_list([[]])

    def test_convert_to_dict(self):
        assert parser._convert_to_dict([1, 2]) == {1: 2}
        assert parser._convert_to_dict({1: 2}) == {1: 2}

        assert_exc([[1, 2], 2, 3], parser._convert_to_dict, TypeError)
        assert_exc(bool, parser._convert_to_dict)

    def test_check_structure(self):
        assert parser.check_structure([1, 2, 3, 4]) == {1: 2, 3: 4}
        assert parser.check_structure({1: 2, 3: 4}) == {1: 2, 3: 4}

        assert_exc(bool, parser.check_structure)
        assert_exc([1, 2, [3], 4], parser.check_structure)
        assert_exc([1, 2, {}, 4], parser.check_structure)
        assert_exc([1, 2, {}, {}], parser.check_structure)
        assert_exc({True: {}, 3: 4}, parser.check_structure)

    def test_field(self):
        f = parser.Field("isbn", "ISBN of the book", "ISBN")
        assert not f.is_valid()

        assert not f.check("ehlo", "xex")
        assert f.value is None
        assert not f.is_valid()

        assert f.check("ISBN knihy", "80-86056-31-7")
        assert f.value == "80-86056-31-7"
        assert f.is_valid()
        assert f.epub == "ISBN"

    def test_field_parser(self):
        f = parser.FieldParser()

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
