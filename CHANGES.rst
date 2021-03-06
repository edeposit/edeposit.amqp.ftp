Changelog
=========

1.0.4
-----
    - Removed ump_templater.py and update_uml.py. Scripts were moved to own repo: https://github.com/edeposit/uml_templater

1.0.0 - 1.0.3
-------------
    - Added some missing tests.
    - Fixed internal log bug.
    - First release version.
    - Minor changes and improvements.
    - ``reactToAMQPMessage()`` parameters modified.
    - isbn.py is no longer part of the edeposit.amqp.aleph, but `standalone module <https://github.com/edeposit/isbn_validator>`_.

0.6.0 - 0.6.4
-------------
    - Into initializer were added checks for linux type - suse requires different settings than ubuntu.
    - Small bugfix in initializer paths.
    - initializer is now standalone script named as edeposit_proftpd_init.py.
    - Fixed bug in passwd_reader.py: missing call to get_ftp_uid().
    - Added checking of the /etc/proftpd/modules.conf file.

0.5.0
-----
    - Added readme.
    - Added Czech and English workflow examples.
    - Fixed bugs in initializer.py.

0.4.0
-----
    - Added almost all documentation.
    - Added a lot of unittests.
    - Created PYPI package.
    - All decoders are now working.
    - Project is almost ready for release version.

0.3.0
-----
    - JSON metadata parser is working.
    - Added basic unittests for metadata decoders.

0.2.0
-----
    - proftpd_monitor.py is almost working, most of the harder algorithms are done.

0.1.0
-----
    - Package created.