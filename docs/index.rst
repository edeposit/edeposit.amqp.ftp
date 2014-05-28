edeposit.amqp.ftp
=================

This module provides wrappers over ProFTPD_ for edeposit_ project. It allows
producers automatic and/or batch uploads of both files and metadata.

.. _ProFTPD: http://www.proftpd.org/
.. _edeposit: http://edeposit.nkp.cz/


Content
-------
Parts of the module can be divided into two subcategories - scripts and parts of
the API.

Scripts are meant to be used by users, API is there mainly for programmers.

Standalone scripts
++++++++++++++++++
.. toctree::

    /api/ftp.monitor
    /api/ftp.initializer


API
+++
.. toctree::
    :maxdepth: 2

    /api/ftp.request_parser
    /api/ftp.api
    /api/ftp.passwd_reader
    /api/ftp.settings
    /api/ftp.structures
    /api/ftp.decoders


Source codes
------------
The project is opensource (GPL) and source codes can be found at GitHub:

- https://github.com/edeposit/edeposit.amqp.ftp

Testing
-------
Almost every feature of the project is tested in unit/integration tests. You
can run this tests using provided script ``run_tests.sh``, which can be found
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
    src/edeposit/amqp/ftp/tests/unittests/test_decoders/test_parser.py .....
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

 