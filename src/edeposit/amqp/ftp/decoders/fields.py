#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================



#= Variables ==================================================================
#= Functions & objects ========================================================
class Field:
    def __init__(self, keyword, description):
        self.keyword = keyword
        self.description = description
        self.value = None

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
            Field(keyword="isbn", description="ISBN"),
            Field(keyword="vazba", description="Vazba/forma"),
            Field(keyword="nazev", description="Název"),
            Field(keyword="misto", description="Místo vydání"),
            Field(keyword="nakladatel", description="Nakladatel"),
            Field(keyword="datum", description="Měsíc a rok vydání"),
            Field(keyword="poradi", description="Pořadí vydání"),
            Field(keyword="zpracovatel", description="Zpracovatel záznamu")
        ]

        self.optional = [
            Field(keyword="url", description="Url"),
            Field(keyword="format", description="Formát"),
            Field(keyword="podnazev", description="Podnázev"),
            Field(keyword="cena", description="Cena"),
        ]

    def process(self, key, val):  # TODO: rename to add()?
        for field in self.fields:
            if field.check(key, val):
                return

        for field in self.optional:
            if field.check(key, val):
                return

    def is_valid(self):
        raise NotImplementedError("Not implemented yet.")

    def get_epublication(self):
        raise NotImplementedError("Not implemented yet.")


#= Main program ===============================================================
if __name__ == '__main__':
    pass
