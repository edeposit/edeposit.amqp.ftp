#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import sys
import os.path

import sh


#= Variables ==================================================================
#= Functions & objects ========================================================
def _read_stdin():
    line = sys.stdin.readline()
    while line:
        yield line
        line = sys.stdin.readline()



def _parse_line(line):
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
    print parsed


def process_file(file_iterator):
    for line in file_iterator:
        if "," not in line or "[" in line:  # TODO: remove [ check
            continue

        parsed = _parse_line(line)

        if not (parsed["command"] in ["STOR", "APPE", "STOU"]):
            continue

        if not os.path.exists(parsed["path"]):
            continue

        process_request(parsed)


#= Main program ===============================================================
if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            process_file(sh.tail("-f", sys.argv[1], _iter=True))
        else:
            process_file(_read_stdin())
    except KeyboardInterrupt:
        sys.exit(0)
