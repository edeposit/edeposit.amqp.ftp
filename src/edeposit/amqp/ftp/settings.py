#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module is containing all necessary global variables for the package.

Module also has the ability to read user-defined data from two paths:

- ``$HOME/_SETTINGS_PATH``
- ``/etc/_SETTINGS_PATH``

See :attr:`._SETTINGS_PATH` for details.

Note:
    If the first path is found, other is ignored.

Example of the configuration file (``$HOME/edeposit/ftp.json``)::

    {
        "CONF_PATH": "/home/bystrousak/.ftpdconf/"
    }

Attributes
----------
"""
import json
import os
import os.path


# Module configuration ========================================================
# Paths =======================================================================
#: Module's path.
BASE_PATH = (os.path.dirname(__file__))

#: Proftpd configuration directory.
CONF_PATH = "/etc/proftpd/"

#: Proftpd log directory.
LOG_PATH = "/var/log/proftpd/"

#: Path to directory, where the user directories will be created.
DATA_PATH = "/home/ftp/"

#: Server's address - used only in unit/integration testing.
SERVER_ADDRESS = "localhost"


# Files =======================================================================
#: Proftpd configuration file (in CONF_PATH directory).
CONF_FILE = CONF_PATH + "proftpd.conf"

#: File where the login informations will be stored (CONF_PATH is used as
#: dirname).
LOGIN_FILE = CONF_PATH + "ftpd.passwd"

MODULES_FILE = CONF_PATH + "modules.conf"

#: File where the extended logs are stored (LOG_PATH is used as dirname).
LOG_FILE = LOG_PATH + "extended.log"

#: Filename for the locking mechanism.
LOCK_FILENAME = "delete_me_to_import_files.txt"

#: Filename, where the error protocol is stored.
USER_ERROR_LOG = "error.log.txt"

#: Filename, where the import protocol for the user is stored.
USER_IMPORT_LOG = "import.log.txt"

#: Text, which will be writen to the PROTFPD_LOCK_FILENAME.
LOCK_FILE_CONTENT = """Delete this file to start batch import of all \
files, you've uploaded to the server.

Smazte tento soubor pro zapoceti davkoveho importu vsech souboru, ktere jste
nahrali na server.
"""


# Switches ====================================================================
#: True - will pair files with same filename in same directory
SAME_NAME_DIR_PAIRING = True

#: True - will pair files with different filenames, if there is only two files
#: in dir
SAME_DIR_PAIRING = True

#: True - if the name is ISBN, files will be paired no matter where they are
#: stored (unless they weren't paired before)
ISBN_PAIRING = True

#: True - Lock file can be only in home directory, everywhere else will be
#: ignored
LOCK_ONLY_IN_HOME = True

#: True - USER_IMPORT_LOG will be created
CREATE_IMPORT_LOG = True

#: True - don't remove badly formatted metadata files
LEAVE_BAD_FILES = True


# Other config ================================================================
#: I am using GID 2000 for all our users - this GID shouldn't be used by other
#: than FTP users!
PROFTPD_USERS_GID = 2000


###############################################################################
# System part, do not edit this ###############################################
###############################################################################
# User configuration merger ===================================================
_ALLOWED_MERGES = [
    "SAME_NAME_DIR_PAIRING",
    "SAME_DIR_PAIRING",
    "ISBN_PAIRING",
    "CREATE_IMPORT_LOG",
    "LEAVE_BAD_FILES",
]


def conf_merger(user_dict, variable):
    """
    Merge global configuration with user's personal configuration.

    Global configuration has always higher priority.
    """
    if variable not in globals().keys():
        raise NameError("Unknown variable '%s'." % variable)

    if variable not in user_dict:
        return globals()[variable]

    return globals()[variable] and user_dict[variable]


# User configuration reader (don't edit this ==================================
_ALLOWED = [str, int, float]

_SETTINGS_PATH = "/edeposit/ftp.json"
"""
Path which is appended to default search paths (``$HOME`` and ``/etc``).

Note:
    It has to start with ``/``. Variable is **appended** to the default search
    paths, so this doesn't mean, that the path is absolute!
"""


def get_all_constants():
    """
    Get list of all uppercase, non-private globals (doesn't start with ``_``).

    Returns:
        list: Uppercase names defined in `globals()` (variables from this \
              module).
    """
    return filter(
        lambda key: key.upper() == key and type(globals()[key]) in _ALLOWED,

        filter(                               # filter _PRIVATE variables
            lambda x: not x.startswith("_"),
            globals()
        )
    )


def substitute_globals(config_dict):
    """
    Set global variables to values defined in `config_dict`.

    Args:
        config_dict (dict): dictionary with data, which are used to set \
                            `globals`.

    Note:
        `config_dict` have to be dictionary, or it is ignored. Also all
        variables, that are not already in globals, or are not types defined in
        :attr:`_ALLOWED` (str, int, float) or starts with ``_`` are silently
        ignored.
    """
    constants = get_all_constants()

    if type(config_dict) != dict:
        return

    for key in config_dict:
        if key in constants and type(config_dict[key]) in _ALLOWED:
            globals()[key] = config_dict[key]


# try to read data from configuration paths ($HOME/_SETTINGS_PATH,
# /etc/_SETTINGS_PATH)
if "HOME" in os.environ and os.path.exists(os.environ["HOME"] + _SETTINGS_PATH):
    with open(os.environ["HOME"] + _SETTINGS_PATH) as f:
        substitute_globals(json.loads(f.read()))
elif os.path.exists("/etc" + _SETTINGS_PATH):
    with open("/etc" + _SETTINGS_PATH) as f:
        substitute_globals(json.loads(f.read()))
