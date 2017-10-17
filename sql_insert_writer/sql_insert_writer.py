# -*- coding: utf-8 -*-

from attrdict import AttrDict
import records

from sqlalchemy.exc import ResourceClosedError


class BadDBNameError(Exception):
    pass


def db_engine_name(db_url):
    result = db_url.split(':')[0].split('+')[0]
    if result == 'postgres':
        result = 'postgresql'
    return result


def col_data_info_schema(db, table_name):
    """Gets metadata for a PostgreSQL table's columns"""

    qry = '''SELECT table_name, column_name, data_type
             FROM information_schema.columns
             WHERE table_name=:table_name
             ORDER BY ordinal_position'''

    return db.query(qry, table_name=table_name).all()


def col_data_sqlite(db, table_name):
    """Gets metadata for a SQLite table's columns"""

    qry = "PRAGMA TABLE_INFO('{}')".format(table_name)
    # Alas cannot use proper parameters here; not recognized in
    # the context of a PRAGMA statement

    db.query(qry)
    curs = db.db.connection.cursor()
    try:
        curs.execute(qry)
        return [AttrDict({'table_name': table_name,
                          'column_name': row.name,
                          'data_type': row.type}) for row in db.query(qry)]
    except ResourceClosedError:  # thus SQLite reacts to nonexistent table
        return []


col_data_functions = {
    'postgresql': col_data_info_schema,
    'sqlite': col_data_sqlite,
    'mysql': col_data_info_schema,
}


def col_data(db, table_name):
    """Gets metadata for a table's columns

    Returns list, each element having .table, name, .column_name, .data_type attributes"""

    db_type = db_engine_name(db.db_url)
    col_data_function = col_data_functions.get(db_type)
    if col_data_function:
        result = col_data_function(db, table_name)
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


def remove_last(target, remove_me):
    """
    Returns string `target` with last occurence of `remove_me` removed

    >>> remove_last('evacuate valorous vampires', 'va')
    'evacuate valorous mpires'
    """

    before = target[:target.rfind(remove_me)]
    after = target[target.rfind(remove_me) + len(remove_me):]
    return before + after


def no_value(db_url):
    """
    Value to insert when no value known; depends on database engine
    """
    if db_engine_name(db_url) == 'postgresql':
        return 'DEFAULT'
    else:
        return 'NULL'


INDENT = ' ' * 2


def build_from_clause(sources):
    """Given a list of table names, connects them with JOINs"""

    from_clause = [sources[0]]
    for join_to in sources[1:]:
        from_clause.append('JOIN {} ON ({}. = {}.)'.format(join_to, sources[0],
                                                           join_to))
    return '\n'.join(from_clause)


def cast(column_str, new_type, db_url):
    'Produces a version of `column_str` cast to data type `new_type` in `db_url` dialtect'
    engine_name = db_engine_name(db_url)
    if engine_name == 'postgresql':
        return '{}::{}'.format(column_str, new_type)
    elif engine_name == 'mysql':
        return 'CAST({} AS {})'.format(column_str, new_type)


def generate_from_tables(db_url,
                         destination,
                         sources,
                         qualify=False,
                         type_cast=False):
    """
    Generates an `INSERT INTO... SELECT FROM` SQL statement.

    Args:
        db_url (str): Database URL in SQLAlchemy format
        destination (str): Name of table to INSERT into
        sources (list): Names of tables to select from, in order of preference
        qualify (bool): Qualify column names with table name even if only one table
        type_cast (bool): Cast values to destination data type where needed

    Returns:
        str: A SQL statement

    """

    db = records.Database(db_url)

    dest_column_block = []
    source_column_block = []

    source_columns = {}
    # Assemble map of {dest col name: dest col}
    for source in reversed(sources):
        # reversed so first-listed source tables overwrite later ones
        for col in col_data(db, source):
            for dest_col_name in [
                    '{table_name}{column_name}'.format(**col),
                    '{table_name}_{column_name}'.format(**col), col.column_name
            ]:
                source_columns[dest_col_name] = col

    qualify = (len(sources) > 1) or qualify
    for dest_col in col_data(db, destination):
        dest_column_block.append(INDENT + dest_col.column_name)
        source_col = source_columns.get(dest_col.column_name)
        if source_col:
            if qualify:
                source_expr = '{}.{}'.format(source_col.table_name,
                                             source_col.column_name)
            else:
                source_expr = source_col.column_name
        else:
            source_expr = no_value(db_url)
        if type_cast and ((not source_col) or
                          source_col.data_type != dest_col.data_type):
            source_expr = cast(source_expr,
                               new_type=dest_col.data_type,
                               db_url=db_url)
        source_column_block.append('{}{},  -- ==> {}'.format(
            INDENT, source_expr, dest_col.column_name))

    dest_column_block = ',\n'.join(dest_column_block)
    source_column_block = '\n'.join(source_column_block)
    source_column_block = remove_last(source_column_block, ',')

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


def generate_from_values(db_url,
                         destination,
                         number_of_tuples=1,
                         type_cast=False):
    """
    Generates an `INSERT INTO... VALUES` SQL statement.

    Args:
        db_url (str): Database URL in SQLAlchemy format
        destination (str): Name of table to INSERT into
        number_of_tuples (int): Number of tuples in VALUES clause
        type_cast (bool): Cast values to destination data type

    Returns:
        str: A SQL statement
    """

    db = records.Database(db_url)

    dest_column_block = []
    source_column_block = []

    for dest_col in col_data(db, destination):
        dest_column_block.append(INDENT + dest_col.column_name)
        source_expr = no_value(db_url)
        if type_cast:
            source_expr = cast(source_expr,
                               new_type=dest_col.data_type,
                               db_url=db_url)
        source_column_block.append('{}{},  -- ==> {}'.format(
            INDENT, source_expr, dest_col.column_name))

    dest_column_block = ',\n'.join(dest_column_block)
    source_column_block = '\n'.join(source_column_block)
    source_column_block = remove_last(source_column_block, ',')
    source_column_blocks = [VALUES_TUPLE_TEMPLATE.format(**locals()),
                            ] * number_of_tuples
    source_column_blocks = ',\n'.join(source_column_blocks)

    return INSERT_FROM_VALUES_TEMPLATE.format(**locals())
