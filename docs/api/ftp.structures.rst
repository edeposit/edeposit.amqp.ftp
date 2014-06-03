ftp.structures module
=====================
.. automodule:: ftp.structures


Requests
--------

.. autoclass:: ftp.structures.AddUser
    :members:

.. autoclass:: ftp.structures.RemoveUser
    :members:

.. autoclass:: ftp.structures.ChangePassword
    :members:

.. autoclass:: ftp.structures.ListRegisteredUsers
    :members:

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

.. autoclass:: ftp.structures.ImportRequest
    :members:

File structures
+++++++++++++++
.. autoclass:: ftp.structures.MetadataFile
    :members:

.. autoclass:: ftp.structures.EbookFile
    :members:

.. autoclass:: ftp.structures.DataPair
    :members:
