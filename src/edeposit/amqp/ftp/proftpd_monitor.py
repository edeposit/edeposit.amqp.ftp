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


def _read_meta_file(fn):
    with open(fn) as f:
        data = f.read()
        return MetadataFile(
            filename=fn,
            raw_data=data,
            parsed_data=decoders.read_meta(data)
        )


def _read_data_file(fn):
    with open(fn) as f:
        data = f.read()
        return EbookFile(filename=fn, raw_data=data)


# TODO: create protocol about import
def process_request(username, path, timestamp):
    items = []
    error_protocol = []

    # lock directory to prevent user to write during processing of the batch
    recursive_chmod(path, 0555)

    # pick up pairs in directories
    for root, dirs, files in os.walk(path):
        for dn in dirs:
            dn = os.path.join(root, dn)
            dir_list = map(lambda fn: dn + "/" + fn, os.listdir(dn))
            files = _filter_files(dir_list)
            files_len = len(files)  # used later, `files` is modified in process
            processed_files = []

            while len(files):
                fn = files.pop()

                # get files with same names (ignore paths and suffixes)
                same_names = _same_named(fn, files)  # returns (index, name)
                indexes = map(lambda (i, fn): i, same_names)  # get indexes
                same_names = map(lambda (i, fn): fn, same_names)  # just names

                # remove `same_names` from `files` (they are processed in this
                # pass)
                for i in sorted(indexes, reverse=True):
                    del files[i]

                if len(same_names) == 1:  # has exactly one file pair
                    ebook = None
                    metadata = None
                    o_fn = same_names[0]

                    if _is_meta(fn) and not _is_meta(o_fn):
                        metadata, ebook = fn, o_fn
                    elif not _is_meta(fn) and _is_meta(o_fn):
                        metadata, ebook = o_fn, fn
                    elif _is_meta(fn) and _is_meta(o_fn):  # both metadata
                        processed_files.extend([fn, o_fn])
                        items.append(_read_meta_file(fn))
                        items.append(_read_meta_file(o_fn))
                    else:  # both data
                        processed_files.extend([fn, o_fn])
                        items.append(_read_data_file(fn))
                        items.append(_read_data_file(o_fn))

                    # process pairs
                    if metadata and ebook:
                        processed_files.extend([metadata, ebook])

                        items.append(
                            DataPair(
                                metadata_file=_read_meta_file(metadata),
                                ebook_file=_read_data_file(ebook)
                            )
                        )
                elif not same_names:  # there is no similar files
                    processed_files.append(fn)

                    if _is_meta(fn):
                        items.append(_read_meta_file(fn))
                    else:
                        items.append(_read_data_file(fn))
                else:  # error - there is too many similar files
                    same_names.append(fn)

                    error_protocol.append(
                        "Too many files with same name:" +
                        "\n\t".join(same_names) + "\n\n---\n"
                    )

            # directory doesn't contain subdirectories
            if len(dir_list) == files_len:
                shutil.rmtree(dn)
            else:
                for fn in processed_files:
                    os.remove(fn)

    # # pick up remaining files
    # for root, dirs, files in os.walk(path):
    #     for fn in files:
    #         pass

    # unlock directory
    recursive_chmod(path, 0775)
    # create_lock_file(path + "/" + PROTFPD_LOCK_FILENAME)

    return items


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

        # old record, which doesn't need to be parsed again
        if os.path.exists(parsed["path"]):
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
