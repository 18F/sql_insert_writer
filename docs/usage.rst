=====
Usage
=====

Used at the command line to auto-generate an INSERT statement.  The generated
statement will generally require some hand-editing for your own purposes, but
the auto-generated column list and comments indicating destinations should save
you tedium and errors.

Specifying database
-------------------

- Accepts `SQLAlchemy database URLs <http://docs.sqlalchemy.org/en/latest/core/engines.html>`_ with `--db` option.
Defaults to environment variable `$DATABASE_URL`

Generally used from the command line.

Sample data
-----------

To try the examples in your own PostgreSQL instance, run the `data setup SQL commands
<sample_tables.sql>`_.

Simple INSERT statements
------------------------

::

    $ sql_insert_writer animal

    INSERT INTO animal (
      id,
      kg,
      species_id
    )
    VALUES
    (
      DEFAULT,  -- ==> id
      DEFAULT,  -- ==> kg
      DEFAULT  -- ==> species_id
    )

Use `--tuples` to insert multiple rows::

    $ sql_insert_writer --tuples 2 animal

    INSERT INTO animal (
      id,
      kg,
      species_id
    )
    VALUES
    (
      DEFAULT,  -- ==> id
      DEFAULT,  -- ==> kg
      DEFAULT  -- ==> species_id
    ),
    (
      DEFAULT,  -- ==> id
      DEFAULT,  -- ==> kg
      DEFAULT  -- ==> species_id
    )

INSERT... FROM
--------------

From a single table::

    $ sql_insert_writer pet animal

    INSERT INTO pet (
      id,
      name,
      kg,
      species_name,
      habitat_name
    )
    SELECT
      id,  -- ==> id
      DEFAULT,  -- ==> name
      kg,  -- ==> kg
      DEFAULT,  -- ==> species_name
      DEFAULT  -- ==> habitat_name
    FROM animal

From multiple tables::

    $ sql_insert_writer pet animal species habitat

    INSERT INTO pet (
      id,
      name,
      kg,
      species_name,
      habitat_name
    )
    SELECT
      animal.id,  -- ==> id
      species.name,  -- ==> name
      animal.kg,  -- ==> kg
      species.name,  -- ==> species_name
      habitat.name  -- ==> habitat_name
    FROM animal
    JOIN species ON (animal. = species.)
    JOIN habitat ON (animal. = habitat.)
