#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import sys


#= Variables ==================================================================



#= Functions & objects ========================================================
def read_stdin():
    while True:
        line = sys.stdin.readline()

        if line:
            yield line
        else:
            break


def parse_line(line):
    line, timestamp = line.rsplit(",", 1)
    line, command = line.rsplit(",", 1)
    path, username = line.rsplit(",", 1)

    return {
        "timestamp": timestamp.strip(),
        "command": command.strip(),
        "username": username.strip(),
        "path": path,
    }

#= Main program ===============================================================
if __name__ == '__main__':
    for line in read_stdin():
        if "," not in line or "[" in line:
            continue

        print parse_line(line)
