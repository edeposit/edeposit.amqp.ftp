AMQP messages/structures
========================
.. automodule:: ftp.structures

Classes from Requests are used to manipulate FTP users. 

Requests
--------

User management requests
++++++++++++++++++++++++

.. image:: /_static/user_management.png

.. autoclass:: ftp.structures.AddUser
    :members:

.. autoclass:: ftp.structures.RemoveUser
    :members:

.. autoclass:: ftp.structures.ChangePassword
    :members:

User requests
+++++++++++++

.. image:: /_static/list_registered_users.png


.. autoclass:: ftp.structures.ListRegisteredUsers
    :members:

Settings management
+++++++++++++++++++

.. image:: /_static/set_get_settings.png

.. autoclass:: ftp.structures.SetUserSettings
    :inherited-members:

.. autoclass:: ftp.structures.GetUserSettings
    :members:

Responses
---------

.. autoclass:: ftp.structures.Userlist
    :members:

.. autoclass:: ftp.structures.UserSettings
    :inherited-members:

Import request
--------------
Import request are sent by :mod:`.monitor` itself, without need of programmer
interaction.

.. image:: /_static/importrequest.png

.. autoclass:: ftp.structures.ImportRequest
    :members:

File structures
+++++++++++++++
Following structures may be present in :attr:`ImportRequest.requests`.

.. autoclass:: ftp.structures.MetadataFile
    :members:

.. autoclass:: ftp.structures.EbookFile
    :members:

.. autoclass:: ftp.structures.DataPair
    :members:
