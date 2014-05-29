__init__.py
===========

This module provides standard interface for AMQP communication as it is defined
and used by :mod:`edeposit.amqp`.

The interface consists of :func:`.reactToAMQPMessage` function, which receives
two parameters - structure and UUID. UUID is not much important, but structure
is usually namedtuple containing information what should module do.

After the work is done, :func:`.reactToAMQPMessage` returns a value, which is
then automatically transfered back to caller. If the exception is raised, it is
also transfered in open and easy to handle way.

.. automodule:: ftp
    :members:
    :undoc-members:
    :show-inheritance:
