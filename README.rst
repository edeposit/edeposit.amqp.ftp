Introduction
============

This module provides wrappers over ProFTPD_ FTP server for edeposit_ project.

It allows producers automatic and/or batch uploads of both files and metadata.
Metadata are recognized and parsed by this package and in case of error, user
is notified by creating special file with error log.

.. _ProFTPD: http://www.proftpd.org/
.. _edeposit: http://edeposit.nkp.cz/

Installation
------------
Module is hosted at `PYPI <https://pypi.python.org/pypi/edeposit.amqp.ftp>`_, and can be easily 
installed using `PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_:

::

    sudo pip install edeposit.amqp.ftp

Source code can be found at `GitHub <https://github.com/>`_: https://github.com/edeposit/edeposit.amqp.ftp

Documentation
-------------
Full module documentation is hosted at ReadTheDocs: http://edeposit-amqp-ftp.readthedocs.org

Content
=======
Content of the module can be divided into two topics - `Scritps` and `API`.

Scripts
-------
edeposit/amqp/ftp/initializer.py
++++++++++++++++++++++++++++++++
Initialization script for ProFTPD and whole package. Run this after installation. 

edeposit/amqp/amqp/ftp/monitor.py
+++++++++++++++++++++++++++++++++
Log monitor. Small wrapper over ``edeposit.amqp.ftp.request_parser`` used mainly for
debugging.

API
---
edeposit.amqp.ftp.api
+++++++++++++++++++++
ProFTPD API. This submodule allows you to create/change/remove FTP users.

edeposit.amqp.ftp.passwd_reader
+++++++++++++++++++++++++++++++
Interface for reading and writing `passwd <https://en.wikipedia.org/wiki/Passwd>`_ files.

edeposit.amqp.ftp.request_parser
++++++++++++++++++++++++++++++++
Extended log reader and reactor.

edeposit.amqp.ftp.decoders
++++++++++++++++++++++++++
Decoders for metadata formats.

edeposit.amqp.ftp.settings
++++++++++++++++++++++++++
Generic settings for all users, paths to log files, users home dir and so on.

edeposit.amqp.ftp.structures
++++++++++++++++++++++++++++
Definitions of all AMQP structures.

AMQP communication
==================
AMQP communication is handled by `edeposit.amqp <https://github.com/edeposit/edeposit.amqp>`_. There are two communication daemons - one that takes care about user management (based at ``edeposit.amqp.ftp.api``) and one that monitors the log and collects all infomations (based at ``edeposit.amqp.amqp.ftp.monitor``).

Tests
=====
This package uses `pytest <http://pytest.org/>`_ for unit and integration test. You can run the tests by calling ``run_tests.sh`` script from the root of the project::

    $ ./run_tests.sh 
    Usage: ./run_tests.sh [-h] [-a] [-i] [-u]

        -h
            Show this help.
        -a
            Run all tests.
        -i
            Run integration test (requires sudo).
        -u
            Run unittest.

For example::

    $ ./run_tests.sh -a
    [sudo] password for bystrousak: 
    ============================= test session starts ==============================
    platform linux2 -- Python 2.7.5 -- py-1.4.20 -- pytest-2.5.2
    collected 42 items 

    src/edeposit/amqp/ftp/tests/integration/test_api.py .....
    src/edeposit/amqp/ftp/tests/integration/test_monitor.py .......
    src/edeposit/amqp/ftp/tests/unittests/test_settings.py .....
    src/edeposit/amqp/ftp/tests/unittests/test_structures.py ...
    src/edeposit/amqp/ftp/tests/unittests/test_unit_monitor.py .
    src/edeposit/amqp/ftp/tests/unittests/test_unit_passwd_reader.py .....
    src/edeposit/amqp/ftp/tests/unittests/test_unit_request_parser.py .....
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_init.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_meta_exceptions.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser_csv.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser_json.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser_xml.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser_yaml.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_validator.py .....

    ========================== 42 passed in 20.56 seconds ==========================
