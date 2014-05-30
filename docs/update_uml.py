#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This script opens all template_* files from _static/ directory, adds values
from structures into "class" declarations and saves them as ``_static/fn.uml``
and ``_static/nn.png``

It is used as documentation generator, because structures can be changed and
I have better things to do than edit the docs.
"""
# Imports =====================================================================
import os
import os.path
import sys
import urllib
import urllib2

sys.path.insert(
    0,
    os.path.normpath(os.path.abspath('.') + '/../src/edeposit/amqp')
)

import conf
import ftp.settings
import ftp.structures


# Variables ===================================================================
STATIC_DIR = conf.html_static_path[0]


# Functions & objects =========================================================
def _get_class_name(line):
    line = line.split("class")[1]
    line = line.split("{")[0]

    return line.strip().split()[0]


def _get_type(var_name):
    if not hasattr(ftp.settings, var_name):
        return type(var_name).__name__
    else:
        return type(getattr(ftp.settings, var_name)).__name__


def _get_png(uml):
    req = urllib2.Request(
        "http://www.plantuml.com/plantuml/form",
        urllib.urlencode({"text": uml})
    )

    data = urllib2.urlopen(req).read()

    image = filter(
        lambda x: 'http://www.plantuml.com:80/plantuml/png/' in x and
                  "<img" in x,
        data.splitlines()
    )[0]
    image = image.split(' src="')[1].split('"')[0]

    return urllib.urlopen(image).read()


def process_uml_file(filename):
    data = None
    with open(filename) as f:
        data = f.read()

    out = []
    for line in data.splitlines():
        out.append(line)

        if not line.strip().startswith("class"):
            continue

        clsn = _get_class_name(line)

        if not hasattr(ftp.structures, clsn):
            continue

        spacer = line.split("class")[0] + "\t"

        out.extend(
            map(
                lambda x: spacer + x + ": " + _get_type(x),
                getattr(ftp.structures, clsn)._fields
            )
        )

    uml = "\n".join(out)
    new_filename = filename.replace("template_", "")

    with open(new_filename, "w") as f:
        f.write(uml)

    with open(new_filename.rsplit(".", 1)[0] + ".png", "wb") as f:
        f.write(_get_png(uml))

    return new_filename


# Main program ================================================================
if __name__ == '__main__':
    for filename in os.listdir(STATIC_DIR):
        filename = STATIC_DIR + "/" + filename
        if not os.path.isfile(filename):
            continue

        if not os.path.basename(filename).startswith("template_"):
            continue

        print filename, "-->", process_uml_file(filename)
