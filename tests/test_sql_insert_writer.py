#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `sql_insert_writer` package."""

import os
import sqlite3
import tempfile

import pytest
import pytest_postgresql

from click import BadOptionUsage
from click.testing import CliRunner

from sql_insert_writer import cli, sql_insert_writer


def dsn_to_url(engine, dsn):
    """
    Converts a DSN to a SQLAlchemy-style database URL

    pytest_postgresql connection only available in DSN form, like
    'dbname=tests user=postgres host=127.0.0.1 port=41663'
    """
    params = dict(s.split('=') for s in dsn.split())
    return '{engine}://{user}@{host}:{port}/{dbname}'.format(engine=engine,
                                                             **params)


TABLE_DEFINITIONS = [
    'CREATE TABLE tab1 (col1 serial primary key, col2 text, col3 text, col4 text)',
    'CREATE TABLE tab2 (col1 serial primary key, col3 text, col4 text)',
    'CREATE TABLE tab3 (col1 serial primary key, col2 text, col4 text)',
    'CREATE TABLE tab4 (col1 serial primary key, col2 text, col3 text)',
]


@pytest.fixture
def pg_db_with_tables(postgresql):
    cur = postgresql.cursor()
    for table_definition in TABLE_DEFINITIONS:
        cur.execute(table_definition)
    postgresql.commit()
    db_url = dsn_to_url('postgresql', postgresql.dsn)
    return db_url


@pytest.fixture
def sqlite_db_with_tables(request):
    sqlite_file = tempfile.NamedTemporaryFile(delete=False)

    def teardown():
        os.unlink(sqlite_file.name)

    request.addfinalizer(teardown)

    conn = sqlite3.connect(sqlite_file.name)
    cur = conn.cursor()
    for table_definition in TABLE_DEFINITIONS:
        cur.execute(table_definition)
    conn.commit()
    return 'sqlite:///' + sqlite_file.name


def _test_generate_from_one_value_tuple(pg_db_with_tables):
    result = sql_insert_writer.generate_from_values(db_url=pg_db_with_tables,
                                                    destination='tab1')
    assert ',  -- ==> col1' in result
    assert '  -- ==> col4' in result


def test_generate_from_one_value_tuple_pg(pg_db_with_tables):
    _test_generate_from_one_value_tuple(pg_db_with_tables)


def test_generate_from_one_value_tuple_sqlite(sqlite_db_with_tables):
    _test_generate_from_one_value_tuple(sqlite_db_with_tables)

# It may be possible to make our fixtures into parameterized fixtures so that
# each test is run against each database engine, but I wasn't able to figure
# out how


def test_generate_multiple_value_tuples(pg_db_with_tables):
    result = sql_insert_writer.generate_from_values(db_url=pg_db_with_tables,
                                                    destination='tab2',
                                                    number_of_tuples=4)

    assert result.count('DEFAULT,  -- ==> col1') == 4
    assert result.count('DEFAULT,  -- ==> col3') == 4
    assert result.count('DEFAULT  -- ==> col4') == 4
    assert result.count('VALUES') == 1


def test_generate_from_one_source(pg_db_with_tables):
    result = sql_insert_writer.generate_from_tables(db_url=pg_db_with_tables,
                                                    destination='tab1',
                                                    sources=['tab2'])
    assert 'col1,  -- ==> col1' in result
    assert 'DEFAULT,  -- ==> col2' in result
    assert 'col3,  -- ==> col3' in result
    assert 'col4  -- ==> col4' in result


def test_generate_from_one_source_with_qualified(pg_db_with_tables):
    result = sql_insert_writer.generate_from_tables(db_url=pg_db_with_tables,
                                                    destination='tab1',
                                                    sources=['tab2'],
                                                    qualify=True)
    assert 'tab2.col1,  -- ==> col1' in result
    assert 'DEFAULT,  -- ==> col2' in result
    assert 'tab2.col3,  -- ==> col3' in result
    assert 'tab2.col4  -- ==> col4' in result


def test_generate_from_three_sources(pg_db_with_tables):
    result = sql_insert_writer.generate_from_tables(
        db_url=pg_db_with_tables,
        destination='tab1',
        sources=['tab2', 'tab3', 'tab4'])
    assert 'tab2.col1,  -- ==> col1' in result
    assert 'tab3.col2,  -- ==> col2' in result
    assert 'tab2.col3,  -- ==> col3' in result
    assert 'tab2.col4  -- ==> col4' in result


def test_generate_from_three_sources_includes_join(pg_db_with_tables):
    result = sql_insert_writer.generate_from_tables(
        db_url=pg_db_with_tables,
        destination='tab1',
        sources=['tab2', 'tab3', 'tab4'])
    assert 'JOIN tab3 ON (tab2' in result


def test_bad_dest_table_name_raises(pg_db_with_tables):
    with pytest.raises(sql_insert_writer.BadDBNameError):
        sql_insert_writer.generate_from_tables(db_url=pg_db_with_tables,
                                               destination='no_such_table',
                                               sources=['tab1'])


def test_bad_source_table_name_raises(pg_db_with_tables):
    with pytest.raises(sql_insert_writer.BadDBNameError):
        sql_insert_writer.generate_from_tables(
            db_url=pg_db_with_tables,
            destination='tab1',
            sources=['tab2', 'no_such_table'])


@pytest.mark.skip
def omit_autoincrementing_primary_keys(pg_db_with_tables):
    assert False


def test_command_line_interface(pg_db_with_tables):
    """Test the CLI."""
    runner = CliRunner()

    # test invoking VALUE insert, one tuple
    result = runner.invoke(cli.main, ['tab1', '--db', pg_db_with_tables])
    assert result.exit_code == 0
    assert 'tab1' in result.output

    # test invoking VALUE insert, two tuples
    result = runner.invoke(cli.main,
                           ['tab1', '--tuples', 2, '--db', pg_db_with_tables])
    assert result.exit_code == 0
    assert 'tab1' in result.output

    # test inserting from one table
    result = runner.invoke(cli.main, ['tab1', 'tab2', '--db',
                                      pg_db_with_tables])
    assert result.exit_code == 0
    assert 'tab2' in result.output

    # test inserting from three tables
    result = runner.invoke(cli.main, ['tab1', 'tab2', 'tab3', 'tab4', '--db',
                                      pg_db_with_tables])
    assert result.exit_code == 0
    assert 'tab2' in result.output

    # # test that using --tuples with source tables raises
    # with pytest.raises(BadOptionUsage):
    #     runner.invoke(cli.main, ['tab1', 'tab2', '--tuples', 2, '--db', pg_db_with_tables])

    # test help
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'source' in help_result.output
