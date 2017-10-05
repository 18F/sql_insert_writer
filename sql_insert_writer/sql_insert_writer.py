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
FROM {source}'''


def find_source_col(dest_col_name, source_metadata):

    if dest_col_name in source_metadata:
        return dest_col_name
    else:
        return 'NULL'


INDENT = ' ' * 2


def generate(db_url, destination, source=None):

    db = records.Database(db_url)

    dest_column_block = []
    source_column_block = []

    source_metadata = {col.column_name: col.data_type
                       for col in col_data(db, source)}
    columns = col_data(db, destination)

    for (row_num, col) in enumerate(columns):
        dest_column_block.append(INDENT + col.column_name)
        if row_num == len(columns) - 1:  # last row, no comma
            comma = ''
        else:
            comma = ','
        source_col_name = find_source_col(col.column_name, source_metadata)
        source_column_block.append('{}{}{}  -- ==> {}'.format(
            INDENT, source_col_name, comma, col.column_name))

    dest_column_block = ',\n'.join(dest_column_block)
    source_column_block = '\n'.join(source_column_block)

    return INSERT_TEMPLATE.format(**locals())
