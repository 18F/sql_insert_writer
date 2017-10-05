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
    assert ', -- ==> col1' in result
    assert ' -- ==> col2' in result


@pytest.mark.skip
def test_generate_with_source(pg_db_with_tables):
    result = sql_insert_writer.generate(db_url=pg_db_with_tables,
                                        destination='tab2',
                                        source='tab1')
    assert 'col1, -- ==> col1' in result
    assert 'col2' not in result
    assert 'NULL, -- ==> col3' in result
    assert 'NULL -- ==> col4' in result


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['my_dest_table'])
    assert result.exit_code == 0
    assert 'my_dest_table' in result.output
    result = runner.invoke(cli.main, ['my_dest_table', '--source',
                                      'my_source_table'])
    assert result.exit_code == 0
    assert 'my_source_table' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'source' in help_result.output
