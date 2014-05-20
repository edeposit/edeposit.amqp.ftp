#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import sys

import os.path
import logging
import argparse

import sh

from settings import *
from request_parser import process_import_request


#= Variables ==================================================================
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.info("Started")


#= Functions & objects ========================================================
def _read_stdin():
    """
    Generator for reading from standard input in nonblocking mode.

    Other ways of reading from ``stdin`` in python waits, until the buffer is
    big enough, or until EOF character is sent.

    This functions yields immediately after each line.
    """
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


def process_log(file_iterator):
    """
    Process the extended ProFTPD log.

    Args:
        file_iterator (file): any file-like iterator for reading the log or
                              stdin (see :funkc:`_read_stdin`).

    Yields:
        ImportRequest: with each import.
    """
    for line in file_iterator:
        if "," not in line:
            continue

        parsed = _parse_line(line)

        if not parsed["command"].upper() in ["DELE", "DEL"]:
            continue

        # don't react to anything else, than trigger in form of deleted
        # "lock" file
        if os.path.basename(parsed["path"]) != LOCK_FILENAME:
            continue

        # react only to lock file in in home directory
        dir_name = os.path.dirname(parsed["path"])
        if LOCK_ONLY_IN_HOME:
            if dir_name != DATA_PATH + parsed["username"]:
                continue

        # deleted user
        if not os.path.exists(os.path.dirname(parsed["path"])):
            continue

        # old record, which doesn't need to be parsed again
        if os.path.exists(parsed["path"]):
            continue

        logger.info(
            "Request for processing from user '%s'." % parsed["username"]
        )

        yield process_import_request(
            username=parsed["username"],
            path=os.path.dirname(parsed["path"]),
            timestamp=parsed["timestamp"],
            logger_handler=logger
        )


def main(filename):
    if filename:
        if not os.path.exists(filename):
            logger.error("'%s' doesn't exists!" % filename)
            sys.stderr.writeln("'%s' doesn't exists!\n" % filename)
            sys.exit(1)

        logger.info("Processing '%s'" % filename)
        for ir in process_log(sh.tail("-f", filename, _iter=True)):
            print ir
    else:
        logger.info("Processing stdin.")
        for ir in process_log(_read_stdin()):
            print ir


#= Main program ===============================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""ProFTPD log monitor. This script reacts to preprogrammed
                       events."""
    )
    parser.add_argument(
        "FN",
        type=str,
        default=None,
        help="""Path to the log file. Usually '%s'. If not set, stdin is used to
                read the log file.""" % LOG_FILE
    )
    parser.add_argument(
        "-v",
        '--verbose',
        action="store_true",
        help="Be verbose."
    )
    parser.add_argument(
        "-vv",
        '--very-verbose',
        action="store_true",
        help="Be very verbose (include debug messages)."
    )
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.INFO)
    if args.very_verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Logger set to debug level.")

    logger.info("Running as standalone program.")
    try:
        main(args.FN)
    except KeyboardInterrupt:
        sys.exit(0)
