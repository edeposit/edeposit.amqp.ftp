#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import os.path
import sys

import sh

from __init__ import ImportRequest, SendEmail
from settings import *
from proftpd_api import set_permissions, create_lock_file


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


def recursive_chmod(path, mode=0755):
    set_permissions(path, mode=mode)
    if os.path.isfile(path):
        return

    for root, dirs, files in os.walk(path):
        for fn in files + dirs:
            set_permissions(os.path.join(root, fn), mode=mode)


def process_request(username, path, timestamp):
    # lock directory to prevent user to write during processing of the batch
    recursive_chmod(path, 0555)

    for root, dirs, files in os.walk(path):
        for fn in files + dirs:
            pass  # TODO: implement file processing

    # unlock directory
    recursive_chmod(path, 0775)
    create_lock_file(path + "/" + PROTFPD_LOCK_FILENAME)


def process_file(file_iterator):
    for line in file_iterator:
        if "," not in line or "[" in line:  # TODO: remove [ check
            continue

        parsed = _parse_line(line)

        if not parsed["command"].upper() in ["DELE", "DEL"]:
            continue

        # don't react to anything else, than trigger in form of deleted
        # "lock" file
        if os.path.basename(parsed["path"]) != PROTFPD_LOCK_FILENAME:
            continue

        yield process_request(
            username=parsed["username"],
            path=os.path.dirname(parsed["path"]),
            timestamp=parsed["timestamp"]
        )


#= Main program ===============================================================
if __name__ == '__main__':
    try:
        it = None
        if len(sys.argv) > 1:
            if not os.path.exists(sys.argv[1]):
                sys.stderr.writeln("'" + sys.argv[1] + "' doesn't exists!\n")
                sys.exit(1)

            it = process_file(sh.tail("-f", sys.argv[1], _iter=True))
        else:
            it = process_file(_read_stdin())

        for request in it:
            print request
    except KeyboardInterrupt:
        sys.exit(0)
