# sql_insert_writer

[![PyPI Status](https://img.shields.io/pypi/v/sql_insert_writer.svg)](https://pypi.python.org/pypi/sql_insert_writer)
[![CircleCI](https://circleci.com/gh/18F/sql_insert_writer.svg?style=svg)](https://circleci.com/gh/18F/sql_insert_writer)
[![Code Climate](https://codeclimate.com/github/18F/sql_insert_writer/badges/gpa.svg)](https://codeclimate.com/github/18F/sql_insert_writer)
[![Test Coverage](https://codeclimate.com/github/18F/sql_insert_writer/badges/coverage.svg)](https://codeclimate.com/github/18F/sql_insert_writer/coverage)
[![Dependency Status](https://gemnasium.com/badges/github.com/18F/sql_insert_writer.svg)](https://gemnasium.com/github.com/18F/sql_insert_writer)

Helps generate highly readable SQL INSERT statements

```
$ sql_insert_writer pet

INSERT INTO pet (
  id,
  name,
  species_name,
  planet,
  kg
)
VALUES
(
  DEFAULT,  -- ==> id
  DEFAULT,  -- ==> name
  DEFAULT,  -- ==> species_name
  DEFAULT,  -- ==> planet
  DEFAULT  -- ==> kg
)

$ sql_insert_writer pet animal

INSERT INTO pet (
  id,
  name,
  species_name,
  planet,
  kg
)
SELECT
  id,  -- ==> id
  name,  -- ==> name
  species_name,  -- ==> species_name
  planet,  -- ==> planet
  DEFAULT  -- ==> kg
FROM animal
```

* Documentation: https://sql-insert-writer.readthedocs.io.

## Rationale

The syntax of `INSERT` statements makes it difficult to tell which destination columns a value is intended for,
especially in inserts with many columns.  (Our five-column example is not bad, but imagine fifty columns!)

Comments can clarify the link between data source and destination, but adding those comments manually is tedious and error-prone.

Explicitly listing the destination columns of an `INSERT` is another best practice often skipped due to tedium.

The output of `sql_insert_writer` will rarely be fully ready to execute, but it should save the bulk of the typing.

## Features

- Supports PostgreSQL, SQLite, MySQL
- Accepts [SQLAlchemy database URLs](http://docs.sqlalchemy.org/en/latest/core/engines.html) with `--db` option.  Defaults to environment variable `$DATABASE_URL`.
- Any number of source tables; columns chosen in order specified
- Any number of tuples in `VALUES` clause with `--tuples` option
- Explicitly cast to destination column type with `--cast` option

## Installtion

[Installation instructions](docs/installation.rst)

## Usage

See usage examples [here](docs/usage.rst)

## Planned features

- Support for more databases
- Approximate column name matches
- Omit inserts into auto-incrementing primary key columns
- Pre-fill JOIN clauses with foreign keys where possible

## Limitations

We do not deal well with case-sensitive table or column names; for lo, they are an abomination unto Codd.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter)
and the [18F/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.

## Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.rst):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
