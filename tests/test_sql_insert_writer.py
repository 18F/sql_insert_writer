#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `sql_insert_writer` package."""

import os
import subprocess
import sqlite3
import tempfile

import pytest
import pytest_postgresql

from click import BadOptionUsage
from click.testing import CliRunner

from sql_insert_writer import cli, sql_insert_writer

try:
    subprocess.check_output('command -v pg_ctl', shell=True)
    PG_CTL_MISSING = False  # sorry for the double-negative, but it's convenient later
except subprocess.CalledProcessError:
    PG_CTL_MISSING = True


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
    'CREATE TABLE tab5 (col1 serial primary key, datecol1 date, intcol1 integer, col2 text)',
    'CREATE TABLE tab5_all_text (col1 serial primary key, datecol1 text, intcol1 text, col2 text)',
    'CREATE TABLE tab_qual_cols (tab3_col2 text, tab4_col2 text)',
]

# pytest-postgresql works locally, but it contains an unshakeable
# assumption that it needs to locally manage postgres instances with
# a local installation of `pg_ctl`, which is incompatible with CircleCI.


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
@pytest.fixture
def pg_url(postgresql):
    cur = postgresql.cursor()
    for table_definition in TABLE_DEFINITIONS:
        cur.execute(table_definition)
    postgresql.commit()
    db_url = dsn_to_url('postgresql', postgresql.dsn)
    return db_url


@pytest.fixture
def sqlite_url(request):
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

# test INSERT... VALUES, one tuple


def _test_generate_from_one_value_tuple(db_url):
    result = sql_insert_writer.generate_from_values(db_url=db_url,
                                                    destination='tab1')
    assert ',  -- ==> col1' in result
    assert '  -- ==> col4' in result


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_generate_from_one_value_tuple_pg(pg_url):
    _test_generate_from_one_value_tuple(pg_url)


def test_generate_from_one_value_tuple_sqlite(sqlite_url):
    _test_generate_from_one_value_tuple(sqlite_url)

# test INSERT... VALUES, multiple tuples


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_generate_multiple_value_tuples_pg(pg_url):
    result = sql_insert_writer.generate_from_values(pg_url,
                                                    destination='tab2',
                                                    number_of_tuples=4)

    assert result.count('DEFAULT,  -- ==> col1') == 4
    assert result.count('DEFAULT,  -- ==> col3') == 4
    assert result.count('DEFAULT  -- ==> col4') == 4
    assert result.count('VALUES') == 1


def test_generate_multiple_value_tuples_sqlite(sqlite_url):
    result = sql_insert_writer.generate_from_values(sqlite_url,
                                                    destination='tab2',
                                                    number_of_tuples=4)

    assert result.count('NULL,  -- ==> col1') == 4
    assert result.count('NULL,  -- ==> col3') == 4
    assert result.count('NULL  -- ==> col4') == 4
    assert result.count('VALUES') == 1

# test INSERT INTO... SELECT..., from one table


def _test_generate_from_one_table(db_url):
    result = sql_insert_writer.generate_from_tables(db_url=db_url,
                                                    destination='tab1',
                                                    sources=['tab2'])
    assert 'col1,  -- ==> col1' in result
    assert 'col3,  -- ==> col3' in result
    assert 'col4  -- ==> col4' in result
    return result


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_generate_from_one_table_pg(pg_url):
    result = _test_generate_from_one_table(pg_url)
    assert 'DEFAULT,  -- ==> col2' in result


def test_generate_from_one_table_sqlite(sqlite_url):
    result = _test_generate_from_one_table(sqlite_url)
    assert 'NULL,  -- ==> col2' in result

# test INSERT INTO... SELECT..., from one table, qualified table names


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def _test_generate_from_one_table_with_qualified(db_url):
    result = sql_insert_writer.generate_from_tables(db_url=db_url,
                                                    destination='tab1',
                                                    sources=['tab2'],
                                                    qualify=True)
    assert 'tab2.col1,  -- ==> col1' in result
    assert 'tab2.col3,  -- ==> col3' in result
    assert 'tab2.col4  -- ==> col4' in result
    return result


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_generate_from_one_table_with_qualified_pg(pg_url):
    result = _test_generate_from_one_table_with_qualified(pg_url)
    assert 'DEFAULT,  -- ==> col2' in result


def test_generate_from_one_table_with_qualified_sqlite(sqlite_url):
    result = _test_generate_from_one_table_with_qualified(sqlite_url)
    assert 'NULL,  -- ==> col2' in result

# test INSERT INTO... SELECT..., from three tables


def _test_generate_from_three_sources(db_url):
    result = sql_insert_writer.generate_from_tables(
        db_url=db_url,
        destination='tab1',
        sources=['tab2', 'tab3', 'tab4'])
    assert 'tab2.col1,  -- ==> col1' in result
    assert 'tab3.col2,  -- ==> col2' in result
    assert 'tab2.col3,  -- ==> col3' in result
    assert 'tab2.col4  -- ==> col4' in result
    assert 'JOIN tab3 ON (tab2' in result


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_generate_from_three_sources_pg(pg_url):
    _test_generate_from_three_sources(pg_url)


def test_generate_from_three_sources_sqlite(sqlite_url):
    _test_generate_from_three_sources(sqlite_url)

# test matching column names with embedded table name


def _test_match_embedded_table_names(db_url):
    """
    Destination table includes source col tables in col names:
    CREATE TABLE tab_qual_cols (tab3_col2 text, tab4_col2 text)
    """
    result = sql_insert_writer.generate_from_tables(db_url=db_url,
                                                    destination='tab_qual_cols',
                                                    sources=['tab3',
                                                             'tab4', ])
    assert 'tab3.col2,  -- ==> tab3_col2' in result
    assert 'tab4.col2  -- ==> tab4_col2' in result


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_match_embedded_table_names_pg(pg_url):
    _test_match_embedded_table_names(pg_url)


def test_match_embedded_table_names_sqlite(sqlite_url):
    _test_match_embedded_table_names(sqlite_url)

# Test nonexistent destination table name throws error


def _test_bad_dest_table_name_raises(db_url):
    with pytest.raises(sql_insert_writer.BadDBNameError):
        sql_insert_writer.generate_from_tables(db_url=db_url,
                                               destination='no_such_table',
                                               sources=['tab1'])


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_bad_dest_table_name_raises_pg(pg_url):
    _test_bad_dest_table_name_raises(pg_url)


def test_bad_dest_table_name_raises_sqlite(sqlite_url):
    _test_bad_dest_table_name_raises(sqlite_url)

# Test nonexistent source table name throws error


def _test_bad_source_table_name_raises(db_url):
    with pytest.raises(sql_insert_writer.BadDBNameError):
        sql_insert_writer.generate_from_tables(
            db_url=db_url,
            destination='tab1',
            sources=['tab2', 'no_such_table'])


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_bad_source_table_name_raises_pg(pg_url):
    _test_bad_source_table_name_raises(pg_url)


def test_bad_source_table_name_raises_sqlite(sqlite_url):
    _test_bad_source_table_name_raises(sqlite_url)


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_type_casting_values_insert(pg_url):
    result = sql_insert_writer.generate_from_values(db_url=pg_url,
                                                    destination='tab5',
                                                    type_cast=True)
    assert 'DEFAULT::date,  -- ==> datecol1' in result
    assert 'DEFAULT::integer,  -- ==> intcol1' in result


@pytest.mark.skipif(PG_CTL_MISSING, reason='PostgreSQL not installed locally')
def test_type_casting_insert_from(pg_url):
    result = sql_insert_writer.generate_from_tables(
        db_url=pg_url,
        destination='tab5',
        sources=['tab5_all_text', ],
        type_cast=True)
    assert 'datecol1::date,  -- ==> datecol1' in result
    assert 'intcol1::integer,  -- ==> intcol1' in result
    assert 'col2  -- ==> col2' in result


@pytest.mark.skip
def omit_autoincrementing_primary_keys(pg_url):
    assert False


def test_command_line_interface(sqlite_url):
    """Test the CLI."""
    runner = CliRunner()

    # test invoking VALUE insert, one tuple
    result = runner.invoke(cli.main, ['tab1', '--db', sqlite_url])
    assert result.exit_code == 0
    assert 'tab1' in result.output

    # test invoking VALUE insert, two tuples
    result = runner.invoke(cli.main,
                           ['tab1', '--tuples', 2, '--db', sqlite_url])
    assert result.exit_code == 0
    assert 'tab1' in result.output

    # test inserting from one table
    result = runner.invoke(cli.main, ['tab1', 'tab2', '--db', sqlite_url])
    assert result.exit_code == 0
    assert 'tab2' in result.output

    # test inserting from three tables
    result = runner.invoke(cli.main, ['tab1', 'tab2', 'tab3', 'tab4', '--db',
                                      sqlite_url])
    assert result.exit_code == 0
    assert 'tab2' in result.output

    # test that using --tuples with source tables raises nonzero exit code
    result = runner.invoke(cli.main, ['tab1', 'tab2', '--tuples', 2, '--db',
                                      sqlite_url])
    assert result.exit_code == 2

    # test help
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'source' in help_result.output
