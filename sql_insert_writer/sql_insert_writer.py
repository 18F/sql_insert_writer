# -*- coding: utf-8 -*-

import os

import records
"""Main module."""


def col_data_pg(db, table_name):
    """Gets metadata for a PostgreSQL table's columns"""

    qry = '''SELECT column_name, data_type
             FROM information_schema.columns
             WHERE table_name=:table_name
             ORDER BY ordinal_position'''

    return db.query(qry, table_name=table_name)


def col_data(db, table_name):
    """Gets metadata for a table's columns"""

    db_type = db.db_url.split(':')[0]
    if db_type.startswith('postgres'):
        return col_data_pg(db, table_name)
    else:
        raise NotImplementedError('{} not supported'.format(db_type))


INSERT_TEMPLATE = '''
INSERT INTO {destination} (
{dest_column_block}
)
SELECT
{source_column_block}
FROM {source}'''


def generate(db_url, destination, source=None):

    db = records.Database(db_url)

    dest_column_block = []
    source_column_block = []

    columns = list(col_data(db, destination))
    for (row_num, col) in enumerate(col_data(db, destination)):
        dest_column_block.append(col.column_name)
        if row_num == len(columns) - 1:  # last row, no comma
            comma = ''
        else:
            comma = ','
        source_column_block.append('{}{} -- ==> {}'.format('NULL', comma,
                                                           col.column_name))

    dest_column_block = ',\n'.join(dest_column_block)
    source_column_block = '\n'.join(source_column_block)

    return INSERT_TEMPLATE.format(**locals())
