#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This submodule provides ability to process and parse import requests.

Most important function in this matter is the :func:`process_import_request`,
which is called from from :func:`ftp.monitor.process_log`. When it is called,
it scans the user's home directory, detects new files, pairs them together into
proper objects (see :mod:`ftp.structures`, speficifally :class:`.MetadataFile`,
:class:`.EbookFile` and :class:`.DataPair`).

API
---
"""
# Imports =====================================================================
import os
import shutil
from collections import namedtuple


try:
    from aleph import isbn
except ImportError:
    from edeposit.amqp.aleph import isbn


import decoders
import passwd_reader
import settings
from settings import conf_merger
from structures import ImportRequest, MetadataFile, EbookFile, DataPair
from api import create_lock_file, recursive_chmod


# Variables ===================================================================
logger = None


# Functions & objects =========================================================
def _filter_files(paths):
    """
    Filter files from the list of `paths`. Directories, symlinks and other crap
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

    Name is taken from the filename and it is just the name of the file,
    without suffix and path.

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

    Name is taken from the filename and it is just the name of the file,
    without suffix and path.

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
    return fn.rsplit(".")[-1].lower() in decoders.SUPPORTED_FILES


def _remove_files(files):
    """
    Remove all given files.

    Args:
        files (list): List of filenames, which will be removed.
    """
    logger.debug("Request for file removal (_remove_files()).")

    for fn in files:
        if os.path.exists(fn):
            logger.debug("Removing '%s'." % fn)
            os.remove(fn)


def _safe_read_meta_file(fn, error_protocol):
    """
    Try to read MetadataFile. If the exception is raised, log the errors to
    the `error_protocol` and return None.
    """
    try:
        return MetadataFile(fn)
    except Exception, e:
        error_protocol.append(
            "Can't read MetadataFile '%s':\n\t%s\n" % (fn, e.message)
        )


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
            _safe_read_meta_file(first_fn, error_protocol),
            _safe_read_meta_file(second_fn, error_protocol)
        ]
    else:                                                 # both data
        logger.debug(
            "Parsed: both '%s' and '%s' as data." % (first_fn, second_fn)
        )
        return [
            EbookFile(first_fn),
            EbookFile(second_fn)
        ]

    # process pairs, which were created in first two branches of the if
    # statement above
    pair = DataPair(
        metadata_file=_safe_read_meta_file(metadata, error_protocol),
        ebook_file=EbookFile(ebook)
    )
    if not pair.metadata_file:
        logger.error(
            "Can't parse MetadataFile '%s'. Continuing with data file '%s'." % (
                metadata, ebook
            )
        )
        return [pair.ebook_file]

    return [pair]


def _process_directory(files, user_conf, error_protocol):
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

    banned = [settings.USER_IMPORT_LOG, settings.USER_ERROR_LOG]
    files = filter(lambda x: not os.path.basename(x) in banned, files)

    if len(files) == 2 and conf_merger(user_conf, "SAME_DIR_PAIRING"):
        logger.debug("There are only two files.")

        items.extend(_process_pair(files[0], files[1], error_protocol))
        files = []

    while files:
        same_names = []
        fn = files.pop()

        logger.debug("Processing '%s'." % fn)

        # get files with same names (ignore paths and suffixes)
        if conf_merger(user_conf, "SAME_NAME_DIR_PAIRING"):
            same_names = _same_named(fn, files)  # returns (index, name)
            indexes = map(lambda (i, fn): i, same_names)  # get indexes
            same_names = map(lambda (i, fn): fn, same_names)  # get names

            # remove `same_names` from `files` (they are processed in this
            # pass)
            for i in sorted(indexes, reverse=True):
                del files[i]

        # has exactly one file pair
        SDP = conf_merger(user_conf, "SAME_NAME_DIR_PAIRING")
        if len(same_names) == 1 and SDP:
            logger.debug(
                "'%s' can be probably paired with '%s'." % (fn, same_names[0])
            )
            items.extend(_process_pair(fn, same_names[0], error_protocol))
        elif not same_names:  # there is no similar files
            logger.debug("'%s' can't be paired. Adding standalone file." % fn)
            if _is_meta(fn):
                items.append(_safe_read_meta_file(fn, error_protocol))
            else:
                items.append(EbookFile(fn))
        else:  # error - there is too many similar files
            logger.error(
                "Too many files with same name: %s" % ", ".join(same_names)
            )
            error_protocol.append(
                "Too many files with same name:" +
                "\n\t".join(same_names) + "\n\n---\n"
            )

    return filter(lambda x: x, items)  # remove None items (errors during read)


def _index(array, item, key=None):
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

        ebook_index = _index(ebooks, meta.name, key=lambda x: x.name)

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


def _create_import_log(items):
    """
    Used to create log with successfully imported data.
    """
    log = []

    for item in items:
        if isinstance(item, MetadataFile):
            log.append(
                "Metadata file '%s' successfully imported." % item.filename
            )
        elif isinstance(item, EbookFile):
            log.append(
                "Ebook file '%s' successfully imported." % item.filename
            )
        elif isinstance(item, DataPair):
            meta = item.metadata_file.filename
            data = item.ebook_file.filename
            log.extend([
                "Metadata and data files paired to epub. import request:",
                "\tMetadata file '%s' successfully imported." % meta,
                "\tEbook file '%s' successfully imported." % data
            ])

    return log


def _process_items(items, user_conf, error_protocol):
    """
    Parse metadata. Remove processed and sucessfully parsed items.

    Returns sucessfully processed items.
    """
    def process_meta(item, error_protocol):
        try:
            return item._parse()
        except Exception, e:
            error_protocol.append(
                "Can't parse %s: %s" % (item._get_filenames()[0], e.message)
            )

            if isinstance(item, DataPair):
                return item.ebook_file

    # process all items and put them to output queue
    out = []
    for item in items:
        if isinstance(item, EbookFile):
            out.append(item)
        else:
            out.append(process_meta(item, error_protocol))
    out = filter(lambda x: x, out)  # remove None items (process_meta() fails)

    # remove processed files
    fn_pool = []
    soon_removed = out if conf_merger(user_conf, "LEAVE_BAD_FILES") else items
    for item in soon_removed:
        fn_pool.extend(item._get_filenames())

    _remove_files(fn_pool)

    return out


def process_import_request(username, path, timestamp, logger_handler):
    """
    React to import request. Look into user's directory and react to files
    user uploaded there.

    Behavior of this function can be set by setting variables in
    :mod:`ftp.settings`.

    Args:
        username (str): Name of the user who triggered the import request.
        path (str): Path to the file, which triggered import request.
        timestamp (float): Timestamp of the event.
        logger_handler (object): Python logger. See :py:mod:`logging` for
                                 details.

    Returns:
        ::class:`.ImportRequest`.
    """
    items = []
    error_protocol = []

    # import logger into local namespace
    global logger
    logger = logger_handler

    # read user configuration
    user_conf = passwd_reader.read_user_config(username)

    # lock directory to prevent user to write during processing of the batch
    logger.info("Locking user´s directory.")
    recursive_chmod(path, 0555)

    try:
        # pick up pairs in directories
        for root, dirs, files in os.walk(path):
            for dn in dirs + [path]:
                dn = os.path.join(root, dn)
                dir_list = map(lambda fn: dn + "/" + fn, os.listdir(dn))
                files = _filter_files(dir_list)

                logger.info("Processing directory '%s'." % dn)

                items.extend(
                    _process_directory(
                        files,
                        user_conf,
                        error_protocol,
                    )
                )

        if conf_merger(user_conf, "ISBN_PAIRING"):
            logger.debug("ISBN_PAIRING is ON.")
            logger.info("Pairing user's files by ISBN filename.")
            items = _isbn_pairing(items)

        # parse metadata and remove files from disk
        items = _process_items(items, user_conf, error_protocol)

        # unlink blank directories left by processing files
        logger.info("Removing blank directories.")
        all_dirs = []
        for root, dirs, files in os.walk(path):
            all_dirs.extend(
                map(lambda x: os.path.join(root, x), dirs)
            )

        for dn in sorted(all_dirs, reverse=True):
            content = os.listdir(dn)
            if not content:
                logger.debug("Removing blank directory '%s'." % dn)
                shutil.rmtree(dn)
            else:
                logger.debug("Leaving non-blank directory: '%s'" % dn)
                logger.debug("Content:\n\t%s" % "\n\t".join(content))

    finally:
        # unlock directory
        logger.info("Unlocking user´s directory.")
        recursive_chmod(path, 0775)
        logger.info("Creating lock file '%s'." % settings.LOCK_FILENAME)
        create_lock_file(path + "/" + settings.LOCK_FILENAME)

        # process errors if found
        if error_protocol:
            logger.error(
                "Found %d error(s)." % len(error_protocol)
            )

            err_path = path + "/" + settings.USER_ERROR_LOG
            with open(err_path, "w") as fh:
                fh.write("\n".join(error_protocol))

            logger.error("Error protocol saved to '%s'." % err_path)

        # process import log
        import_log = _create_import_log(items)
        if import_log and conf_merger(user_conf, "CREATE_IMPORT_LOG"):
            logger.debug("CREATE_IMPORT_LOG is on.")

            imp_path = path + "/" + settings.USER_IMPORT_LOG
            with open(imp_path, "w") as f:
                if error_protocol:
                    f.write("Status: Error\n\n")
                    f.write("Error: Import only partially successful.\n")
                    f.write(
                        "See '%s' for details.\n" % settings.USER_ERROR_LOG
                    )
                    f.write("\n--- Errors ---\n")
                    f.write("\n".join(error_protocol))
                    f.write("\n\n--- Successfully imported files ---\n")
                else:
                    f.write("Status: Ok\n\n")
                    f.write("--- Sucess ---\n")
                f.write("\n".join(import_log))

            logger.info("Created import protocol '%s'." % imp_path)

    return ImportRequest(
        username=username,
        requests=items,
        import_log="\n".join(import_log),
        error_log="\n".join(error_protocol)
    )
