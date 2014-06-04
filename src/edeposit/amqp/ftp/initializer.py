#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports ====================================================================
import os
import os.path
import sys
from pwd import getpwnam

from settings import CONF_PATH, CONF_FILE, DATA_PATH, LOGIN_FILE, LOG_FILE
from api import reload_configuration, require_root


# Variables ==================================================================
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


# Functions & objects ========================================================,
def add_or_update(data, item, value):
    """
    Add or update value in configuration file format used by proftpd.

    Args:
        data (str): Configuration file as string.
        item (str): What option will be added/updated.
        value (str): Value of option.

    Returns:
        (string): updated configuration
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


@require_root
def main():
    """
    Used to create configuration files, set permissions and so on.
    """
    if not os.path.exists(CONF_PATH):
        pass  # TODO: create/unpack default configuration

    # check existence of proftpd.conf
    if not os.path.exists(CONF_FILE):
        with open(CONF_FILE, "w") as f:
            f.write(DEFAULT_PROFTPD_CONF)

    # create data directory, where the user informations will be stored
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH, 0777)

    # create user files if they doesn't exists
    if not os.path.exists(LOGIN_FILE):
        open(LOGIN_FILE, "a").close()

    os.chown(LOGIN_FILE, getpwnam('proftpd').pw_uid, -1)
    os.chmod(LOGIN_FILE, 0400)

    # load values from protpd conf file
    data = ""
    with open(CONF_FILE) as f:
        data = f.read()

    # set path to passwd file
    data = add_or_update(
        data,
        "AuthUserFile",
        LOGIN_FILE
    )
    data = add_or_update(data, "RequireValidShell", "off")
    data = add_or_update(data, "DefaultRoot", "~")

    # http://www.proftpd.org/docs/modules/mod_log.html
    data = add_or_update(data, "LogFormat", 'paths "%f, %u, %m, %{%s}t"')
    data = add_or_update(
        data,
        "ExtendedLog",
        LOG_FILE + " WRITE paths"
    )

    # save changed file
    with open(CONF_FILE, "w") as f:
        f.write(data)

    reload_configuration()


# Main program ===============================================================
if __name__ == '__main__':
    main()
