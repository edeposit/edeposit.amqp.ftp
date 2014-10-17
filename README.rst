Introduction
============

.. image:: https://badge.fury.io/py/edeposit.amqp.ftp.png
    :target: http://badge.fury.io/py/edeposit.amqp.ftp

.. image:: https://pypip.in/d/edeposit.amqp.ftp/badge.png
        :target: https://crate.io/packages/edeposit.amqp.ftp?version=latest

This module provides wrappers over ProFTPD_ FTP server for edeposit_ project.

It allows producers automatic and/or batch uploads of both files and metadata.
Metadata are recognized and parsed by this package and in case of error, user
is notified by creating special file with error log.

.. _ProFTPD: http://www.proftpd.org/
.. _edeposit: http://edeposit.nkp.cz/

Documentation
-------------

Full module documentation and description can be found at Read the Docs:

- http://edeposit-amqp-ftp.readthedocs.org/