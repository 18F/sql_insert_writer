# -*- coding: utf-8 -*-
"""Console script for sql_insert_writer."""

import click
from sql_insert_writer import sql_insert_writer


@click.command()
@click.argument('destination')
@click.option('--db',
              envvar='DATABASE_URL',
              help='Database URL, RFC-1738 / SQLAlchemy format')
@click.option('--source', default=None, help='Table to SELECT values from')
def main(destination, db, source):
    """Console script for sql_insert_writer."""
    click.echo("Source: {} --> Dest: {}".format(source, destination))
    result = sql_insert_writer.generate(db, destination, source)
    click.echo(result)


if __name__ == "__main__":
    main()
