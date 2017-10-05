# -*- coding: utf-8 -*-

import os

import records
"""Main module."""


class BadDBNameError(Exception):
    pass


def col_data_pg(db, table_name):
    """Gets metadata for a PostgreSQL table's columns"""

    qry = '''SELECT column_name, data_type
             FROM information_schema.columns
             WHERE table_name=:table_name
             ORDER BY ordinal_position'''

    return db.query(qry, table_name=table_name)


def col_data(db, table_name):
    """Gets metadata for a table's columns"""

    if not table_name:
        return []  # but do not raise, because we knew there would be none

    db_type = db.db_url.split(':')[0]
    if db_type.startswith('postgres'):
        result = col_data_pg(db, table_name).all()
    else:
        raise NotImplementedError('{} not supported'.format(db_type))

    if len(result) == 0:
        raise BadDBNameError('No table {} in database'.format(table_name))

    return result


INSERT_TEMPLATE = '''
INSERT INTO {destination} (
{dest_column_block}
)
SELECT
{source_column_block}
FROM {from_clause}'''


def no_value():
    """
    Value to insert when no value known
    """
    return 'DEFAULT'


def find_source_col(dest_col_name, source_metadata, qualify):

    if dest_col_name in source_metadata:
        if qualify:
            return '{}.{}'.format(source_metadata[dest_col_name]['source'],
                                  dest_col_name)
        else:
            return dest_col_name
    else:
        return no_value()


INDENT = ' ' * 2


def build_from_clause(sources):
    """Given a list of table names, connects them with JOINs"""

    from_clause = [sources[0]]
    for join_to in sources[1:]:
        from_clause.append('JOIN {} ON ({}. = {}.)'.format(
            join_to, sources[0], join_to))
    return '\n'.join(from_clause)


def generate_from_tables(db_url, destination, sources, qualify=False):
    """
    Generates an `INSERT INTO... SELECT FROM` SQL statement.

    Args:
        db_url (str): Database URL in SQLAlchemy format
        destination (str): Name of table to INSERT into
        sources (list): Names of tables to select from, in order of preference
        qualify (bool): Qualify column names with table name even if only one table

    Returns:
        str: A SQL statement

    """

    db = records.Database(db_url)

    dest_column_block = []
    source_column_block = []

    # Each column should have only one source - sources listed first take
    # precedence
    source_columns = {}
    for source in reversed(sources):
        source_metadata = {col.column_name: {'source': source,
                                             'type': col.data_type}
                           for col in col_data(db, source)}
        source_columns.update(source_metadata)

    columns = col_data(db, destination)
    qualify = (len(sources) > 1) or qualify
    for (row_num, col) in enumerate(columns):
        dest_column_block.append(INDENT + col.column_name)
        if row_num == len(columns) - 1:  # last row, no comma
            comma = ''
        else:
            comma = ','
        source_col_name = find_source_col(col.column_name, source_columns,
                                          qualify)
        source_column_block.append('{}{}{}  -- ==> {}'.format(
            INDENT, source_col_name, comma, col.column_name))

    dest_column_block = ',\n'.join(dest_column_block)
    source_column_block = '\n'.join(source_column_block)

    from_clause = build_from_clause(sources)

    return INSERT_TEMPLATE.format(**locals())


VALUES_TUPLE_TEMPLATE = '''(
{source_column_block}
)'''

INSERT_FROM_VALUES_TEMPLATE = '''
INSERT INTO {destination} (
{dest_column_block}
)
VALUES
{source_column_blocks}'''


def generate_from_values(db_url, destination, number_of_tuples=1):
    """
    Generates an `INSERT INTO... VALUES` SQL statement.

    Args:
        db_url (str): Database URL in SQLAlchemy format
        destination (str): Name of table to INSERT into
        number_of_tuples (int): Number of tuples in VALUES clause

    Returns:
        str: A SQL statement
    """

    db = records.Database(db_url)

    dest_column_block = []
    source_column_block = []

    columns = col_data(db, destination)

    for (row_num, col) in enumerate(columns):
        dest_column_block.append(INDENT + col.column_name)
        if row_num == len(columns) - 1:  # last row, no comma
            comma = ''
        else:
            comma = ','
        source_column_block.append('{}{}{}  -- ==> {}'.format(INDENT, no_value(
        ), comma, col.column_name))

    dest_column_block = ',\n'.join(dest_column_block)
    source_column_block = '\n'.join(source_column_block)
    source_column_blocks = [VALUES_TUPLE_TEMPLATE.format(**locals()),
                            ] * number_of_tuples
    source_column_blocks = ',\n'.join(source_column_blocks)

    return INSERT_FROM_VALUES_TEMPLATE.format(**locals())
