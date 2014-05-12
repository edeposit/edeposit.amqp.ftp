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
import logging
import argparse

import sh

try:
    from aleph import isbn
except ImportError:
    from edeposit.amqp.aleph import isbn

import decoders
from settings import *
from structures import *
from __init__ import ImportRequest
from proftpd_api import set_permissions, create_lock_file


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


def recursive_chmod(path, mode=0755):
    """
    Recursively change ``mode`` for given ``path``. Same as 'chmod -R `mode`'.

    Args:
        path (str): Path of the directory/file.
        mode (octal int, default 0755): New mode of the file. Don't forget to
                                        add ``0`` at the beginning of the
                                        numbers, or Unspeakable HoRrOrS will be
                                        awaken from their unholy sleep outside
                                        of the reality and they WILL eat your
                                        soul (and your files).
    """
    set_permissions(path, mode=mode)
    if os.path.isfile(path):
        return

    # recursively change mode of all subdirectories
    for root, dirs, files in os.walk(path):
        for fn in files + dirs:
            set_permissions(os.path.join(root, fn), mode=mode)


def _filter_files(paths):
    """
    Filter files from the list of path. Directories, symlinks and other crap
    (named pipes and so on) are ignored.

    Args:
        paths (list): List of string paths.

    Return (list): Paths, which points to files.
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
    """
    Return ``True``, if the `fn` argument looks (has right suffix) like it can
    be meta.
    """
    if "." not in fn:
        return False
    return fn.rsplit(".")[1].lower() in decoders.SUPPORTED_FILES


def _remove_files(files):
    """
    Remove all given files.

    Args:
        files (list): List of filenames, which will be removed.
    """
    for fn in files:
        logger.debug("Removing '%s'." % fn)
        os.remove(fn)


def _safe_parse_meta_file(fn, error_protocol):
    """
    Try to parse MetadataFile. If the exception is raised, log the errors to
    the `error_protocol` and return blank ``list``.
    """
    try:
        return [parse_meta_file(fn)]
    except decoders.MetaParsingException, e:
        error_protocol.append(
            "Can't parse MetadataFile '%s':\n\t%s\n" % (fn, e.value)
        )

    return []


def _process_pair(first_fn, second_fn, error_protocol):
    """
    Look at given filenames, decide which is what and try to pair them.
    """
    ebook = None
    metadata = None

    if _is_meta(first_fn) and not _is_meta(second_fn):    # 1st meta, 2nd data
        logger.debug(
            "Parsed: '%s' as meta, '%s' as data." % (first_fn, second_fn)
        )
        metadata, ebook = first_fn, second_fn
    elif not _is_meta(first_fn) and _is_meta(second_fn):  # 1st data, 2nd meta
        logger.debug(
            "Parsed: '%s' as meta, '%s' as data." % (second_fn, first_fn)
        )
        metadata, ebook = second_fn, first_fn
    elif _is_meta(first_fn) and _is_meta(second_fn):      # both metadata
        logger.debug(
            "Parsed: both '%s' and '%s' as meta." % (first_fn, second_fn)
        )
        return [
            _safe_parse_meta_file(first_fn, error_protocol),
            _safe_parse_meta_file(second_fn, error_protocol)
        ]
    else:                                                 # both data
        logger.debug(
            "Parsed: both '%s' and '%s' as data." % (first_fn, second_fn)
        )
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
        logger.error("Can't parse MetadataFile '%s': %s" % (fn, e.value))
        error_protocol.append(
            "Can't parse MetadataFile '%s':\n\t%s\n" % (fn, e.value)
        )

    return [pair]


def _process_directory(dn, files, error_protocol, dir_size, path):
    """
    Look at items in given directory, try to match them for same names and pair
    them.

    If the items can't be paired, add their representation.

    Note:
        All successfully processed files are removed.

    Returns:
        list: of items. Example: [MetadataFile, DataPair, DataPair, EbookFile]
    """
    items = []
    files_len = len(files)  # used later, `files` is modified in process
    processed_files = []

    if len(files) == 2 and PROFTPD_SAME_DIR_PAIRING:
        logger.debug("There are only two files.")

        items.extend(_process_pair(files[0], files[1], error_protocol))
        processed_files.extend(files)
        files = []

    while files:
        same_names = []
        fn = files.pop()

        logger.debug("Processing '%s'." % fn)

        # get files with same names (ignore paths and suffixes)
        if PROFTPD_SAME_NAME_DIR_PAIRING:
            same_names = _same_named(fn, files)  # returns (index, name)
            indexes = map(lambda (i, fn): i, same_names)  # get indexes
            same_names = map(lambda (i, fn): fn, same_names)  # get names

            # remove `same_names` from `files` (they are processed in this pass)
            for i in sorted(indexes, reverse=True):
                del files[i]

        if len(same_names) == 1:  # has exactly one file pair
            logger.debug(
                "'%s' can be probably paired with '%s'." % (fn, same_names[0])
            )
            items.extend(_process_pair(fn, same_names[0], error_protocol))
            processed_files.extend([fn, same_names[0]])
        elif not same_names:  # there is no similar files
            logger.debug("'%s' can't be paired. Adding standalone file." % fn)
            if _is_meta(fn):
                items.extend(_safe_parse_meta_file(fn, error_protocol))
            else:
                items.append(parse_data_file(fn))
            processed_files.append(fn)
        else:  # error - there is too many similar files
            logger.error(
                "Too many files with same name: %s" % ", ".join(same_names)
            )
            error_protocol.append(
                "Too many files with same name:" +
                "\n\t".join(same_names) + "\n\n---\n"
            )
            processed_files.append(fn)

    logger.info("Removing processed files.")
    if dir_size == files_len:   # directory doesn't contain subdirs
        if dn != path:          # don't remove root directory (user home)
            logger.debug("Removing whole directory '%s'." % dn)
            shutil.rmtree(dn)
        else:
            _remove_files(processed_files)
    else:
        _remove_files(processed_files)

    return items


def index(array, item, key=None):
    """
    Array search function.

    Written, because ``.index()`` method for array doesn't have `key` parameter
    and raises `ValueError`, if the item is not found.

    Args:
        array (list): List of items, which will be searched.
        item (whatever): Item, which will be matched to elements in `array`.
        key (function, default None): Function, which will be used for lookup
                                      into each element in `array`.

    Return:
        Index of `item` in `array`, if the `item` is in `array`, else `-1`.
    """
    for i, el in enumerate(array):
        resolved_el = key(el) if key else el

        if resolved_el == item:
            return i

    return -1


def _isbn_pairing(items):
    """
    Pair `items` with same ISBN into `DataPair` objects.

    Args:
        items (list): list of items, which will be searched.

    Returns:
        list: list with paired items. Paired items are removed, `DataPair` is \
              added instead.
    """
    NameWrapper = namedtuple("NameWrapper", ["name", "obj"])
    metas = map(
        lambda x: NameWrapper(_just_name(x.filename), x),
        filter(lambda x: isinstance(x, MetadataFile), items)
    )
    ebooks = map(
        lambda x: NameWrapper(_just_name(x.filename), x),
        filter(lambda x: isinstance(x, EbookFile), items)
    )

    # simple pairing mechanism, which shouldn't be O^2 complex, but something
    # slightly better
    metas = sorted(metas, key=lambda x: x.name)
    ebooks = sorted(ebooks, key=lambda x: x.name, reverse=True)
    while metas:
        meta = metas.pop()

        if not isbn.is_valid_isbn(meta.name):
            continue

        if not ebooks:
            break

        ebook_index = index(ebooks, meta.name, key=lambda x: x.name)

        if ebook_index >= 0:
            logger.debug(
                "Pairing '%s' and '%s'." % (
                    meta.obj.filename,
                    ebooks[ebook_index].obj.filename
                )
            )
            items.append(
                DataPair(
                    metadata_file=meta.obj,
                    ebook_file=ebooks[ebook_index].obj
                )
            )
            items.remove(meta.obj)
            items.remove(ebooks[ebook_index].obj)
            ebooks = ebooks[ebook_index+1:]

    return items


# TODO: create protocol about import
# TODO: wrap critical part in try..finally block
def process_import_request(username, path, timestamp):
    items = []
    error_protocol = []  # TODO: use logging?

    # lock directory to prevent user to write during processing of the batch
    logger.info("Locking user´s directory.")
    recursive_chmod(path, 0555)

    # pick up pairs in directories
    for root, dirs, files in os.walk(path):
        for dn in dirs + [path]:
            dn = os.path.join(root, dn)
            dir_list = map(lambda fn: dn + "/" + fn, os.listdir(dn))
            files = _filter_files(dir_list)

            logger.info("Processing directory '%s'." % dn)

            items.extend(
                _process_directory(
                    dn,
                    files,
                    error_protocol,
                    len(dir_list),
                    path
                )
            )

    if PROFTPD_ISBN_PAIRING:
        logger.debug("PROFTPD_ISBN_PAIRING is ON.")
        logger.info("Pairing user's files by ISBN filename.")
        items = _isbn_pairing(items)

    # unlink blank directories left by processing files
    logger.info("Removing blank directories.")
    for root, dirs, files in os.walk(path):
        for dn in dirs:
            dn = os.path.join(root, dn)
            if not os.listdir(dn):
                logger.debug("Removing blank directory '%s'." % dn)
                shutil.rmtree(dn)

    # unlock directory
    logger.info("Unlocking user´s directory.")
    recursive_chmod(path, 0775)
    logger.info("Creating lock file '%s'." % PROFTPD_LOCK_FILENAME)
    create_lock_file(path + "/" + PROFTPD_LOCK_FILENAME)

    if error_protocol:
        logger.error(
            "Found %d error(s). Saving error protocol." % len(error_protocol)
        )

        err_path = path + "/" + PROFTPD_USER_ERROR_LOG
        with open(err_path, "wt") as f:
            f.write("\n".join(error_protocol))

        logger.error("Error protocol saved to '%s'." % err_path)

    return ImportRequest(
        username=username,
        requests=items
    )


def process_log(file_iterator):
    for line in file_iterator:
        if "," not in line:
            continue

        parsed = _parse_line(line)

        if not parsed["command"].upper() in ["DELE", "DEL"]:
            continue

        # don't react to anything else, than trigger in form of deleted
        # "lock" file
        if os.path.basename(parsed["path"]) != PROFTPD_LOCK_FILENAME:
            continue

        # react only to lock file in in home directory
        dir_name = os.path.dirname(parsed["path"])
        if PROFTPD_LOCK_ONLY_IN_HOME:
            if dir_name != PROFTPD_DATA_PATH + parsed["username"]:
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
            timestamp=parsed["timestamp"]
        )


def main(args):
    if args.FN:
        if not os.path.exists(sys.argv[1]):
            logger.error("'%s' doesn't exists!" % args.FN)
            sys.stderr.writeln("'%s' doesn't exists!\n" % args.FN)
            sys.exit(1)

        logger.info("Processing '%s'" % args.FN)
        for ir in process_log(sh.tail("-f", args.FN, _iter=True)):
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
                read the log file.""" % PROFTPD_LOG_FILE
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

    if args.verbose:  # TODO: zprovoznit
        logger.setLevel(logging.INFO)
    if args.very_verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Logger set to debug level.")

    logger.info("Runnig as standalone program.")
    try:
        main(args)
    except KeyboardInterrupt:
        sys.exit(0)
