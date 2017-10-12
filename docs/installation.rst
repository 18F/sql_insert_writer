.. highlight:: shell

============
Installation
============


Stable release
--------------

To install sql_insert_writer, run this command in your terminal:

.. code-block:: console

    $ pip install sql-insert-writer

This is the preferred method to install sql_insert_writer, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for sql_insert_writer can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/18F/sql_insert_writer

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/18F/sql_insert_writer/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

Requirements
------------

Pip or setup.py should automatically download and install all prerequisites,
except for a Python database driver package, which should be installed
for the database you are using:

PostgreSQL: `pip install psycopg2`

SQLite3: (No install necessary)


.. _Github repo: https://github.com/18F/sql_insert_writer
.. _tarball: https://github.com/18F/sql_insert_writer/tarball/master
