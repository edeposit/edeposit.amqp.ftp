#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This script is used to initialize ProFTPD and set configuration required by
edeposit.amqp.ftp module.

It changes/creates ProFTPD configuration file, password file and extened log
file. Also user directory is created and correct permissions is set.
"""
# Imports ====================================================================
import os
import sys
import shutil
import os.path
import logging
import argparse

# if the module wasn't yet installed at this system
try:
    import edeposit.amqp.ftp
except ImportError:
    sys.path.insert(0, os.path.abspath('../src/edeposit/amqp'))
    import ftp
    sys.modules["edeposit.amqp.ftp"] = ftp

from edeposit.amqp.ftp.api import reload_configuration, require_root
from edeposit.amqp.ftp.passwd_reader import get_ftp_uid
from edeposit.amqp.ftp.settings import CONF_PATH, CONF_FILE, DATA_PATH
from edeposit.amqp.ftp.settings import LOGIN_FILE, LOG_FILE, MODULES_FILE


# Variables ==================================================================
logging.basicConfig()
logger = logging.getLogger(__name__)


DEFAULT_PROFTPD_CONF = r"""
#
# /etc/proftpd/proftpd.conf -- This is a basic ProFTPD configuration file.
# To really apply changes, reload proftpd after modifications, if
# it runs in daemon mode. It is not required in inetd/xinetd mode.
#

# Includes DSO modules
Include /etc/proftpd/modules.conf

# Set off to disable IPv6 support which is annoying on IPv4 only boxes.
UseIPv6             on
# If set on you can experience a longer connection delay in many cases.
IdentLookups            off

ServerName          "Debian"
ServerType          standalone
DeferWelcome            off

MultilineRFC2228        on
DefaultServer           on
ShowSymlinks            on

TimeoutNoTransfer       600
TimeoutStalled          600
TimeoutIdle             1200

DisplayLogin            welcome.msg
DisplayChdir            .message true
ListOptions             "-l"

DenyFilter              \*.*/

# Use this to jail all users in their homes
DefaultRoot ~

# Users require a valid shell listed in /etc/shells to login.
# Use this directive to release that constrain.
RequireValidShell off

# Port 21 is the standard FTP port.
Port                21

# In some cases you have to specify passive ports range to by-pass
# firewall limitations. Ephemeral ports can be used for that, but
# feel free to use a more narrow range.
# PassivePorts                  49152 65534

# If your host was NATted, this option is useful in order to
# allow passive tranfers to work. You have to use your public
# address and opening the passive ports used on your firewall as well.
# MasqueradeAddress     1.2.3.4

# This is useful for masquerading address with dynamic IPs:
# refresh any configured MasqueradeAddress directives every 8 hours
<IfModule mod_dynmasq.c>
# DynMasqRefresh 28800
</IfModule>

# To prevent DoS attacks, set the maximum number of child processes
# to 30.  If you need to allow more than 30 concurrent connections
# at once, simply increase this value.  Note that this ONLY works
# in standalone mode, in inetd mode you should use an inetd server
# that allows you to limit maximum number of processes per service
# (such as xinetd)
MaxInstances            30

# Set the user and group that the server normally runs at.
User                proftpd
Group               nogroup

# Umask 022 is a good standard umask to prevent new files and dirs
# (second parm) from being group and world writable.
Umask               022  022
# Normally, we want files to be overwriteable.
AllowOverwrite          on

# Uncomment this if you are using NIS or LDAP via NSS to retrieve passwords:
# PersistentPasswd      off

# This is required to use both PAM-based authentication and local passwords
# AuthOrder         mod_auth_pam.c* mod_auth_unix.c

# Be warned: use of this directive impacts CPU average load!
# Uncomment this if you like to see progress and transfer rate with ftpwho
# in downloads. That is not needed for uploads rates.
#
# UseSendFile           off

TransferLog /var/log/proftpd/xferlog
SystemLog   /var/log/proftpd/proftpd.log

# Logging onto /var/log/lastlog is enabled but set to off by default
#UseLastlog on

# In order to keep log file dates consistent after chroot, use timezone info
# from /etc/localtime.  If this is not set, and proftpd is configured to
# chroot (e.g. DefaultRoot or <Anonymous>), it will use the non-daylight
# savings timezone regardless of whether DST is in effect.
#SetEnv TZ :/etc/localtime

<IfModule mod_quotatab.c>
QuotaEngine off
</IfModule>

<IfModule mod_ratio.c>
Ratios off
</IfModule>


# Delay engine reduces impact of the so-called Timing Attack described in
# http://www.securityfocus.com/bid/11430/discuss
# It is on by default.
<IfModule mod_delay.c>
DelayEngine on
</IfModule>

<IfModule mod_ctrls.c>
ControlsEngine        off
ControlsMaxClients    2
ControlsLog           /var/log/proftpd/controls.log
ControlsInterval      5
ControlsSocket        /var/run/proftpd/proftpd.sock
</IfModule>

<IfModule mod_ctrls_admin.c>
AdminControlsEngine off
</IfModule>

# Alternative authentication frameworks
#
#Include /etc/proftpd/ldap.conf
#Include /etc/proftpd/sql.conf

# This is used for FTPS connections
#
#Include /etc/proftpd/tls.conf

# Useful to keep VirtualHost/VirtualRoot directives separated
#
Include /etc/proftpd/virtuals.conf

# Include other custom configuration files
Include /etc/proftpd/conf.d/

AuthUserFile /etc/proftpd/ftpd.passwd
"""

DEFAULT_MODULES_CONF = r"""
# This file is used to manage DSO modules and features.
#

# This is the directory where DSO modules reside

ModulePath /usr/lib/proftpd

# Allow only user root to load and unload modules, but allow everyone
# to see which modules have been loaded

ModuleControlsACLs insmod,rmmod allow user root
ModuleControlsACLs lsmod allow user *

LoadModule mod_ctrls_admin.c
LoadModule mod_tls.c

# Install one of proftpd-mod-mysql, proftpd-mod-pgsql or any other
# SQL backend engine to use this module and the required backend.
# This module must be mandatory loaded before anyone of
# the existent SQL backeds.
#LoadModule mod_sql.c

# Install proftpd-mod-ldap to use this
#LoadModule mod_ldap.c

#
# 'SQLBackend mysql' or 'SQLBackend postgres' (or any other valid backend)
# directives are required to have SQL authorization working. You can also
# comment out the unused module here, in alternative.
#

# Install proftpd-mod-mysql and decomment the previous
# mod_sql.c module to use this.
#LoadModule mod_sql_mysql.c

# Install proftpd-mod-pgsql and decomment the previous
# mod_sql.c module to use this.
#LoadModule mod_sql_postgres.c

# Install proftpd-mod-sqlite and decomment the previous
# mod_sql.c module to use this
#LoadModule mod_sql_sqlite.c

# Install proftpd-mod-odbc and decomment the previous
# mod_sql.c module to use this
#LoadModule mod_sql_odbc.c

# Install one of the previous SQL backends and decomment
# the previous mod_sql.c module to use this
#LoadModule mod_sql_passwd.c

LoadModule mod_radius.c
LoadModule mod_quotatab.c
LoadModule mod_quotatab_file.c

# Install proftpd-mod-ldap to use this
#LoadModule mod_quotatab_ldap.c

# Install one of the previous SQL backends and decomment
# the previous mod_sql.c module to use this
#LoadModule mod_quotatab_sql.c
LoadModule mod_quotatab_radius.c
LoadModule mod_wrap.c
LoadModule mod_rewrite.c
#LoadModule mod_sql_odbcad.c
LoadModule mod_ban.c
LoadModule mod_wrap2.c
LoadModule mod_wrap2_file.c
# Install one of the previous SQL backends and decomment
# the previous mod_sql.c module to use this
#LoadModule mod_wrap2_sql.c
LoadModule mod_dynmasq.c
LoadModule mod_exec.c
LoadModule mod_shaper.c
LoadModule mod_ratio.c
LoadModule mod_site_misc.c

LoadModule mod_sftp.c
LoadModule mod_sftp_pam.c
# Install one of the previous SQL backends and decomment
# the previous mod_sql.c module to use this
#LoadModule mod_sftp_sql.c

LoadModule mod_facl.c
LoadModule mod_unique_id.c
LoadModule mod_copy.c
LoadModule mod_deflate.c
LoadModule mod_ifversion.c
LoadModule mod_tls_memcache.c

# Install proftpd-mod-geoip to use the GeoIP feature
#LoadModule mod_geoip.c

#LoadModule mod_log.c

# keep this module the last one
LoadModule mod_ifsession.c
"""


# Functions & objects ========================================================,
def add_or_update(data, item, value):
    """
    Add or update value in configuration file format used by proftpd.

    Args:
        data (str): Configuration file as string.
        item (str): What option will be added/updated.
        value (str): Value of option.

    Returns:
        str: updated configuration
    """
    data = data.splitlines()

    # to list of bytearrays (this is useful, because their reference passed to
    # other functions can be changed, and it will change objects in arrays
    # unlike strings)
    data = map(lambda x: bytearray(x), data)

    # search for the item in raw (ucommented) values
    conf = filter(lambda x: x.strip() and x.strip().split()[0] == item, data)

    if conf:
        conf[0][:] = conf[0].strip().split()[0] + " " + value
    else:
        # search for the item in commented values, if found, uncomment it
        comments = filter(
            lambda x: x.strip().startswith("#")
                      and len(x.split("#")) >= 2
                      and x.split("#")[1].split()
                      and x.split("#")[1].split()[0] == item,
            data
        )

        if comments:
            comments[0][:] = comments[0].split("#")[1].split()[0] + " " + value
        else:
            # add item, if not found in raw/commented values
            data.append(item + " " + value + "\n")

    return "\n".join(map(lambda x: str(x), data))  # convert back to string


def comment(data, what):
    """
    Comments line containing `what` in string `data`.

    Args:
        data (str): Configuration file in string.
        what (str): Line which will be commented out.

    Returns:
        str: Configuration file with commented `what`.
    """
    data = data.splitlines()

    data = map(
        lambda x: "#" + x if x.strip().split() == what.split() else x,
        data
    )

    return "\n".join(data)


def _is_deb_system():
    """
    Badly written test whether the system is deb/apt based or not.
    """
    return os.path.exists("/etc/apt")


def _write_conf_file():
    """
    Write configuration file as it is defined in settings.
    """
    with open(CONF_FILE, "w") as f:
        f.write(DEFAULT_PROFTPD_CONF)
        logger.debug("'%s' created.", CONF_FILE)


@require_root
def main(overwrite):
    """
    Used to create configuration files, set permissions and so on.
    """
    logger.debug("Checking existence of '%s'.", CONF_PATH)
    if not os.path.exists(CONF_PATH):
        logger.debug("Directory %s not found! Panicking..", CONF_PATH)
        raise UserWarning(
            "Can't find '%s' - it looks like ProFTPD is not installed!" % (
                CONF_PATH,
            )
        )

    # check existence of proftpd.conf
    logger.debug("Checking existence of configuration file '%s'.", CONF_FILE)
    if not os.path.exists(CONF_FILE):
        logger.debug("Configuration file not found, creating..")
        _write_conf_file()
    else:
        logger.debug("Found.")

        if not os.path.exists(CONF_FILE + "_"):
            logger.debug(
                "Backing up the configuration file '%s' -> '%s'.",
                CONF_FILE,
                CONF_FILE + "_"
            )
            shutil.copyfile(CONF_FILE, CONF_FILE + "_")
        else:
            logger.debug(
                "Backup already exists. '%s' will be overwritten.",
                CONF_FILE
            )
    if overwrite:
        logger.debug("--update switch not found, overwriting conf file")
        _write_conf_file()

    logger.debug("Checking existence of the '%s' file.", MODULES_FILE)
    if not os.path.exists(MODULES_FILE) and _is_deb_system():
        with open(MODULES_FILE, "w") as f:
            f.write(DEFAULT_MODULES_CONF)
            logger.debug("Modules file not found. Created '%s'.", MODULES_FILE)

    # create data directory, where the user informations will be stored
    logger.debug("Checking existence of user's directory '%s'.", DATA_PATH)
    if not os.path.exists(DATA_PATH):
        logger.debug("Directory '%s' not found, creating..", DATA_PATH)

        os.makedirs(DATA_PATH, 0777)

        logger.debug("Done. '%s' created.", DATA_PATH)

    # create user files if they doesn't exists
    logger.debug("Checking existence of passwd file '%s'.", LOGIN_FILE)
    if not os.path.exists(LOGIN_FILE):
        logger.debug("passwd file not found, creating..")

        open(LOGIN_FILE, "a").close()

        logger.debug("Done. '%s' created.")

    logger.debug("Setting permissions..")
    os.chown(LOGIN_FILE, get_ftp_uid(), -1)
    os.chmod(LOGIN_FILE, 0400)

    # load values from protpd conf file
    logger.debug("Switching and adding options..")
    data = ""
    with open(CONF_FILE) as f:
        data = f.read()

    # set path to passwd file
    logger.debug("\tAuthUserFile")
    data = add_or_update(
        data,
        "AuthUserFile",
        LOGIN_FILE
    )
    logger.debug("\tRequireValidShell")
    data = add_or_update(data, "RequireValidShell", "off")
    logger.debug("\tDefaultRoot")
    data = add_or_update(data, "DefaultRoot", "~")

    # http://www.proftpd.org/docs/modules/mod_log.html
    logger.debug("\tLogFormat")
    data = add_or_update(data, "LogFormat", 'paths "%f, %u, %m, %{%s}t"')
    logger.debug("\tExtendedLog")
    data = add_or_update(
        data,
        "ExtendedLog",
        LOG_FILE + " WRITE paths"
    )

    if not _is_deb_system():
        logger.debug("Detected non debian based linux. Aplying SUSE changes.")
        data = comment(data, "IdentLookups off")
        data = comment(data, "Include /etc/proftpd/modules.conf")
        data = add_or_update(data, "User", "ftp")

    # save changed file
    logger.debug("Saving into config file..")
    with open(CONF_FILE, "w") as f:
        f.write(data)
        logger.debug("Done.")

    logger.debug("Sending proftpd signal to reload configuration..")
    reload_configuration()
    logger.debug("Done.")
    logger.info("All set.")


# Main program ===============================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""This script will modify your ProFTPD installation for
                       use with edeposit.amqp.ftp package."""
    )
    parser.add_argument(
        "-o",
        '--overwrite',
        action="store_true",
        help="""Overwrite ProFTPD configuration file with edeposit.amqp.ftp
                default configuration."""
    )
    parser.add_argument(
        "-v",
        '--verbose',
        action="store_true",
        help="Print debug output."
    )
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Logger set to debug level.")
    else:
        logger.setLevel(logging.INFO)

    try:
        main(args.overwrite)
    except (AssertionError, UserWarning) as e:
        sys.stderr.write(e.message + "\n")
        sys.exit(1)
