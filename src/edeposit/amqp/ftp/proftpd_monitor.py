#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import sys
import os.path

import sh

from __init__ import ImportRequest, SendEmail


#= Variables ==================================================================
#= Functions & objects ========================================================
def _read_stdin():
    line = sys.stdin.readline()
    while line:
        yield line
        line = sys.stdin.readline()


def _parse_line(line):
    # typical line looks like this;
    # /home/ftp/xex/asd bsd.dat, xex, STOR, 1398351777
    # filename may contain ',' character, so I am rsplitting the line from the
    # end to the beginning
    line, timestamp = line.rsplit(",", 1)
    line, command = line.rsplit(",", 1)
    path, username = line.rsplit(",", 1)

    return {
        "timestamp": timestamp.strip(),
        "command": command.strip(),
        "username": username.strip(),
        "path": path,
    }


def process_request(parsed):
    if not os.path.exists(parsed["path"]):
        return

    data = ""
    with open(parsed["path"]) as f:
        data = f.read()

    if not data.strip():
        return SendEmail(
            username=parsed["username"],
            subject="Blank export data",
            text=""
        )


def process_file(file_iterator):
    for line in file_iterator:
        if "," not in line or "[" in line:  # TODO: remove [ check
            continue

        parsed = _parse_line(line)

        if not (parsed["command"] in ["STOR", "APPE", "STOU"]):
            continue

        if not os.path.exists(parsed["path"]):
            continue

        yield process_request(parsed)


#= Main program ===============================================================
if __name__ == '__main__':
    try:
        it = None
        if len(sys.argv) > 1:
            it = process_file(sh.tail("-f", sys.argv[1], _iter=True))
        else:
            it = process_file(_read_stdin())

        for request in it:
            print request
    except KeyboardInterrupt:
        sys.exit(0)
