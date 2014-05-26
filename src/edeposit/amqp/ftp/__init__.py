#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
# from settings import *
import api
import structures
import passwd_reader


# Variables ===================================================================
# Functions & objects =========================================================
def _instanceof(instance, cls):
    """
    Check type of `instance` by matching ``.__name__`` with `cls.__name__`.
    """
    return type(instance).__name__ == cls.__name__


# Main function ===============================================================
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
    if _instanceof(message, structures.AddUser):
        api.add_user(
            username=message.username,
            password=message.password
        )
        return True  # TODO: předělat na něco užitečnějšího? je to zapotřebí?
    elif _instanceof(message, structures.RemoveUser):
        api.remove_user(message.username)
        return True
    elif _instanceof(message, structures.ChangePassword):
        api.change_password(
            username=message.username,
            new_password=message.new_password
        )
        return True
    elif _instanceof(message, structures.ListRegisteredUsers):
        return structures.Userlist(api.list_users())
    elif _instanceof(message, structures.SetUserSettings):
        username = message.username

        # convert namedtuple to dict (python rocks)
        conf_dict = dict(message._asdict())
        del conf_dict["username"]

        passwd_reader.save_user_config(
            username,
            conf_dict
        )

        conf_dict = passwd_reader.read_user_config(username)
        conf_dict["username"] = username
        return structures.UserSettings(**conf_dict)
    elif _instanceof(message, structures.GetUserSettings):
        conf_dict = passwd_reader.read_user_config(message.username)
        conf_dict["username"] = message.username
        return structures.UserSettings(**conf_dict)

    raise ValueError(
        "Unknown type of request: '" + str(type(message)) + "'!"
    )
