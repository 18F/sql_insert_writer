#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `sql_insert_writer` package."""

import pytest
import pytest_postgresql

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


@pytest.fixture
def pg_db_with_tables(postgresql):
    cur = postgresql.cursor()
    cur.execute('CREATE TABLE tab1 (col1 serial primary key, col2 text)')
    cur.execute(
        'CREATE TABLE tab2 (col1 serial primary key, col3 text, col4 text)')
    postgresql.commit()
    db_url = dsn_to_url('postgresql', postgresql.dsn)
    return db_url


def test_generate_no_source(pg_db_with_tables):
    result = sql_insert_writer.generate(db_url=pg_db_with_tables,
                                        destination='tab1')
    assert ',  -- ==> col1' in result
    assert '  -- ==> col2' in result


def test_generate_with_source(pg_db_with_tables):
    result = sql_insert_writer.generate(db_url=pg_db_with_tables,
                                        destination='tab2',
                                        source='tab1')
    assert 'col1,  -- ==> col1' in result
    assert 'col2' not in result
    assert 'NULL,  -- ==> col3' in result
    assert 'NULL  -- ==> col4' in result


def test_bad_dest_column_raises(pg_db_with_tables):
    with pytest.raises(sql_insert_writer.BadDBNameError):
        sql_insert_writer.generate(db_url=pg_db_with_tables,
                                   destination='no_such_table')


def test_bad_source_column_raises(pg_db_with_tables):
    with pytest.raises(sql_insert_writer.BadDBNameError):
        sql_insert_writer.generate(db_url=pg_db_with_tables,
                                   destination='tab1',
                                   source='no_such_table')


def test_command_line_interface(pg_db_with_tables):
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['tab1', '--db', pg_db_with_tables])
    assert result.exit_code == 0
    assert 'tab1' in result.output
    result = runner.invoke(cli.main, ['tab1', '--source', 'tab2', '--db',
                                      pg_db_with_tables])
    assert result.exit_code == 0
    assert 'tab2' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'source' in help_result.output
