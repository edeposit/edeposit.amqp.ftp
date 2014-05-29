#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This script opens all template_* files from _static/ directory, adds values
from structures into them and saves them as _static/fn.uml and f_static/n.png

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


def process_uml_file(fn):
    data = None
    with open(fn) as f:
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
    nfn = fn.replace("template_", "")

    with open(nfn, "w") as f:
        f.write(uml)

    with open(nfn.rsplit(".", 1)[0] + ".png", "wb") as f:
        f.write(_get_png(uml))

    return nfn


# Main program ================================================================
if __name__ == '__main__':
    for fn in os.listdir(STATIC_DIR):
        fn = STATIC_DIR + "/" + fn
        if not os.path.isfile(fn):
            continue

        if not os.path.basename(fn).startswith("template_"):
            continue

        print fn, "-->", process_uml_file(fn)
