# -*- coding: utf-8 -*-
"""Console script for sql_insert_writer."""

import click
from sql_insert_writer import sql_insert_writer


@click.command()
@click.version_option()
@click.argument('destination')
@click.argument('sources', nargs=-1)
@click.option('-d', '--db',
              envvar='DATABASE_URL',
              help='Database URL, RFC-1738 / SQLAlchemy format')
@click.option('-t', '--tuples',
              type=click.IntRange(min=1),
              default=1,
              help='Number of VALUES tuples')
@click.option('--qualify/--no-qualify',
              default=False,
              help='Include source table name even if only one source')
@click.option('--cast/--no-cast',
              default=False,
              help='CAST values as destination data type')
def main(destination, sources, db, tuples, qualify, cast):
    """Console script for sql_insert_writer."""
    if sources:
        if tuples > 1:
            raise click.BadOptionUsage('Use --tuples only when no source tables specified')
        result = sql_insert_writer.generate_from_tables(
            db_url=db,
            destination=destination,
            sources=sources,
            qualify=qualify,
            type_cast=cast)
    else:
        result = sql_insert_writer.generate_from_values(
            db_url=db,
            destination=destination,
            number_of_tuples=tuples,
            type_cast=cast)
    click.echo(result)


if __name__ == "__main__":
    main()
