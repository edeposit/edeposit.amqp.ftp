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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

 