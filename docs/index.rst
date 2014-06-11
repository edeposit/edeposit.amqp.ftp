edeposit.amqp.ftp
=================

This module provides wrappers over ProFTPD_ FTP server for edeposit_ project.

It allows producers automatic and/or batch uploads of both files and metadata.
Metadata are recognized and parsed by this package and in case of error, user
is notified by creating special file with error log.

.. _ProFTPD: http://www.proftpd.org/
.. _edeposit: http://edeposit.nkp.cz/


Installation
------------
This module is hosted at PIP, so you can install it easily with following
command::

    sudo pip install edeposit.amqp.ftp

This will install the module and all necessary requirements with one exception
- the ProFTPD server itself. That can be installed manually or using package
manager from your distribution.

Ubuntu/Debian::

    sudo apt-get install proftpd-basic proftpd-mod-vroot

OpenSuse::

    sudo zypper install proftpd

Initialization
++++++++++++++
After installation of the ``ProFTPD`` and ``edeposit.amqp.ftp``, run the
:doc:`edeposit_proftpd_init.py </initializer>` script (should be in your path),
which will configure ProFTPD and create all necessary files and directories.

Depending at which system are you using, you may need to restart/reload the
``proftpd`` daemon.

You may also want to check :mod:`.settings` module, to change some of the paths
using JSON configuration files.

Usage
-----
There is guide how to use the package from user perspective:

- :doc:`/workflow/workflow` (english version)
- :doc:`/workflow/pouziti` (czech version)

Content
-------
.. image:: /_static/relations.png
    :width: 600px


Parts of the module can be divided into two subcategories - scripts and parts of
the API.

Scripts are meant to be used by users, API is there mainly for programmers.


Standalone scripts
++++++++++++++++++
.. toctree::
    :maxdepth: 1

    /initializer
    /api/ftp.monitor


API
+++
.. toctree::
    :maxdepth: 1

    /api/ftp
    /api/ftp.request_parser
    /api/ftp.api
    /api/ftp.passwd_reader
    /api/ftp.structures
    /api/ftp.decoders
    /api/ftp.settings


Source code
-----------
The project is opensource (GPL) and source codes can be found at GitHub:

- https://github.com/edeposit/edeposit.amqp.ftp

Testing
-------
Almost every feature of the project is tested in unit/integration tests. You
can run this tests using provided ``run_tests.sh`` script, which can be found
in the root of the project.

Requirements
++++++++++++
This script expects that pytest_ is installed. In case you don't have it yet,
it can be easily installed using following command::

    pip install --user pytest

or for all users::

    sudo pip install pytest

.. _pytest: http://pytest.org/


Options
+++++++
Script provides three options - to run just unittests (``-u`` switch), to run
integration tests (``-i`` switch) or to run both (``-a`` switch).

Integration tests requires that ProFTPD is installed (there is test to test
this) and also **root permissions**. Integration tests are trying all usual
(and some unusual) use-cases, permissions to read/write into ProFTPD 
configuration files and so on. Thats why the root access is required.

Example of the success output from test script::

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
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_validator.py .....
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser_csv.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser_json.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser_xml.py .
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser_yaml.py .

    ========================== 42 passed in 13.96 seconds ==========================


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

 