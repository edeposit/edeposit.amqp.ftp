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


#= Variables ==================================================================
#= Functions & objects ========================================================
class Field:
    def __init__(self, keyword, descr, epub=None):
        self.keyword = keyword
        self.descr = descr
        self.value = None
        self.epub = epub if epub is not None else self.keyword

    def check(self, key, value):
        if self.keyword in key.lower().strip():
            self.value = value
            return True

        return False

    def is_valid(self):
        return self.value is not None


class FieldValidator:
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

    def process(self, key, val):  # TODO: rename to add()?
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

            raise ValueError("Missing fields:\n\t" + "\n\t".join(bad_fields))

        relevant_fields = self.fields
        relevant_fields += filter(lambda x: x.is_valid(), self.optional)

        epub_dict = dict(map(lambda x: (x.epub, x.value), relevant_fields))

        return EPublication(
            ISBN=epub_dict.get("ISBN", None),
            nazev=epub_dict.get("nazev", None),
            podnazev=epub_dict.get("podnazev", None),
            vazba=epub_dict.get("vazba", None),
            cena=epub_dict.get("cena", None),
            castDil=epub_dict.get("castDil", None),
            nazevCasti=epub_dict.get("nazevCasti", None),
            nakladatelVydavatel=epub_dict.get("nakladatelVydavatel", None),
            datumVydani=epub_dict.get("datumVydani", None),
            poradiVydani=epub_dict.get("poradiVydani", None),
            zpracovatelZaznamu=epub_dict.get("zpracovatelZaznamu", None),
            format=epub_dict.get("format", None),
            url=epub_dict.get("url", None),
            mistoVydani=epub_dict.get("mistoVydani", None),
            ISBNSouboruPublikaci=epub_dict.get("ISBNSouboruPublikaci", None),
            autori=epub_dict.get("autori", None),
            originaly=epub_dict.get("originaly", None),
            internal_url=epub_dict.get("internal_url", None),
        )
