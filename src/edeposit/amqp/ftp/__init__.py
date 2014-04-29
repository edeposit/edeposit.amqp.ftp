
#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import sh

from settings import *
from structures import *


#= Variables ==================================================================
#= Functions & objects ========================================================
def reload_configuration():
    sh.killall("-HUP", "proftpd", _ok_code=[0, 1])


def _instanceof(instance, class_):
    """Check type by matching ``.__name__``."""
    return type(instance).__name__ == class_.__name__


#= Main function ==============================================================
def reactToAMQPMessage(message, UUID):
    """
    React to given (AMQP) message. `message` is usually expected to be
    :py:func:`collections.namedtuple` structure filled with all necessary data.

    Args:
        message (.. class): TODO: ..

        UUID (str):                unique ID of received message

    Returns:
        : response TODO: comment when the protocol will be ready

    Raises:
        ValueError: if bad type of `message` structure is given.
    """
    if _instanceof(message, CreateUser):
        pass  # TODO: ..

    raise ValueError(
        "Unknown type of request: '" + str(type(message)) + "'!"
    )
