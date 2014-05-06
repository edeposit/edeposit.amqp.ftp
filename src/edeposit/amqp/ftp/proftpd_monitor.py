#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import sys
import shutil
import os.path

import sh

import decoders
from settings import *
from structures import *
from __init__ import ImportRequest, SendEmail
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

    # recursively change mode of all subdirectories
    for root, dirs, files in os.walk(path):
        for fn in files + dirs:
            set_permissions(os.path.join(root, fn), mode=mode)


def _filter_files(paths):
    """
    Args:
        paths (list): list of string paths

    Return (list): paths, which points to files.
    """
    return filter(
        lambda path: os.path.isfile(path),
        paths
    )


def _just_name(fn):
    """
    Return: (str) `name` for given `fn`.

    Name is taken from the filename and it is just the name of the file, without
    suffix and path.

    For example - name of ``/home/bystrousak/config.json`` is just ``config``.
    """
    fn = os.path.basename(fn)  # get filename
    return fn.rsplit(".", 1)[0]  # get name without suffix


def _same_named(fn, fn_list):
    """
    Args:
        fn (str): Matching filename.
        fn_list (list): List of filenames.

    Return: (list of tuples) filenames from `fn_list`, which has same *name* as
    `fn` and their indexes in tuple (i, fn).

    Name is taken from the filename and it is just the name of the file, without
    suffix and path.

    For example - name of ``/home/bystrousak/config.json`` is just ``config``.
    """
    fn = _just_name(fn)

    return filter(
        lambda (i, filename): fn == _just_name(filename),
        enumerate(fn_list)
    )


def _is_meta(fn):
    if "." not in fn:
        return False
    return fn.rsplit(".")[1].lower() in decoders.SUPPORTED_FILES


def _remove_files(files):
    for fn in files:
        os.remove(fn)


def _safe_parse_meta_file(fn, error_protocol):
    try:
        return [parse_meta_file(fn)]
    except decoders.MetaParsingException, e:
        error_protocol.append(
            "Can't parse MetadataFile '%s':\n\t%s\n" % (fn, e.value)
        )

    return []


def _process_pair(first_fn, second_fn, error_protocol):
    ebook = None
    metadata = None

    if _is_meta(first_fn) and not _is_meta(second_fn):    # 1st meta, 2nd data
        metadata, ebook = first_fn, second_fn
    elif not _is_meta(first_fn) and _is_meta(second_fn):  # 1st data, 2nd meta
        metadata, ebook = second_fn, first_fn
    elif _is_meta(first_fn) and _is_meta(second_fn):      # both metadata
        return [
            _safe_parse_meta_file(first_fn, error_protocol),
            _safe_parse_meta_file(second_fn, error_protocol)
        ]
    else:                                                 # both data
        return [
            parse_data_file(first_fn),
            parse_data_file(second_fn)
        ]

    # process pairs, which were created in first two branches
    # of the if statement above
    pair = None
    try:
        pair = DataPair(
            metadata_file=parse_meta_file(metadata),
            ebook_file=parse_data_file(ebook)
        )
    except decoders.MetaParsingException, e:
        pair = parse_data_file(ebook)
        error_protocol.append(
            "Can't parse MetadataFile '%s':\n\t%s\n" % (fn, e.value)
        )

    return [pair]


def _process_directory(dn, files, error_protocol):
    items = []
    files_len = len(files)  # used later, `files` is modified in process
    processed_files = []

    if len(files) == 2 and PROFTPD_SAME_DIR_PAIRING:
        items.extend(_process_pair(files[0], files[1]))
        processed_files.extend(files)
        files = []

    while files:
        same_names = []
        fn = files.pop()

        # get files with same names (ignore paths and suffixes)
        if PROFTPD_SAME_NAME_DIR_PAIRING:
            same_names = _same_named(fn, files)  # returns (index, name)
            indexes = map(lambda (i, fn): i, same_names)  # get indexes
            same_names = map(lambda (i, fn): fn, same_names)  # get names

            # remove `same_names` from `files` (they are processed in this pass)
            for i in sorted(indexes, reverse=True):
                del files[i]

        if len(same_names) == 1:  # has exactly one file pair
            items.extend(_process_pair(fn, same_names[0]))
            processed_files.extend([fn, same_names[0]])
        elif not same_names:  # there is no similar files
            if _is_meta(fn):
                items.extend(_safe_parse_meta_file(fn, error_protocol))
            else:
                items.append(parse_data_file(fn))
            processed_files.append(fn)
        else:  # error - there is too many similar files
            error_protocol.append(
                "Too many files with same name:" +
                "\n\t".join(same_names) + "\n\n---\n"
            )
            processed_files.append(fn)

    if len(dir_list) == files_len:  # directory doesn't contain subdirs
        if dn != path:              # don't remove root directory (user home)
            shutil.rmtree(dn)
        else:
            _remove_files(processed_files)
    else:
        _remove_files(processed_files)

    return items


# TODO: create protocol about import
# TODO: párování na základě ISBN
def process_import_request(username, path, timestamp):
    items = []
    error_protocol = []  # TODO: use logging?

    # lock directory to prevent user to write during processing of the batch
    recursive_chmod(path, 0555)

    # pick up pairs in directories
    for root, dirs, files in os.walk(path):
        for dn in dirs + [path]:
            dn = os.path.join(root, dn)
            dir_list = map(lambda fn: dn + "/" + fn, os.listdir(dn))
            files = _filter_files(dir_list)

            items.extend(_process_directory(dn, files, error_protocol))

    # unlink blank directories left by processing files
    for root, dirs, files in os.walk(path):
        for dn in dirs:
            dn = os.path.join(root, dn)
            if not os.listdir(dn):
                shutil.rmtree(dn)

    # unlock directory
    recursive_chmod(path, 0775)
    # create_lock_file(path + "/" + PROFTPD_LOCK_FILENAME)

    if error_protocol:
        with open(PROFTPD_USER_ERROR_LOG, "wt") as f:
            f.write("\n".join(error_protocol))

    return items  # TODO: ImportRequest


def process_log(file_iterator):
    for line in file_iterator:
        if "," not in line or "[" in line:  # TODO: remove [ check
            continue

        parsed = _parse_line(line)

        if not parsed["command"].upper() in ["DELE", "DEL"]:
            continue

        # don't react to anything else, than trigger in form of deleted
        # "lock" file
        if os.path.basename(parsed["path"]) != PROFTPD_LOCK_FILENAME:
            continue

        # TODO: allow only trigger in home directory (or settings configurable?)

        # old record, which doesn't need to be parsed again
        if os.path.exists(parsed["path"]):
            continue

        yield process_import_request(
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

            it = process_log(sh.tail("-f", sys.argv[1], _iter=True))
        else:
            it = process_log(_read_stdin())

        for request in it:
            print request
    except KeyboardInterrupt:
        sys.exit(0)
