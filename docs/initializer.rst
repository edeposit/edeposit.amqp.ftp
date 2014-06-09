Initializer script
==================

.. automodule:: edeposit_proftpd_init
    :show-inheritance:

Usage
-----

::

    $ ./edeposit_proftpd_init.py -h
    usage: edeposit_proftpd_init.py [-h] [-o] [-v]

    This script will modify your ProFTPD installation for use with
    edeposit.amqp.ftp package.

    optional arguments:
      -h, --help       show this help message and exit
      -o, --overwrite  Overwrite ProFTPD configuration file with edeposit.amqp.ftp
                       default configuration.
      -v, --verbose    Print debug output.


API
---

.. autofunction:: edeposit_proftpd_init.main

.. autofunction:: edeposit_proftpd_init.add_or_update
