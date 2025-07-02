import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('sql.db')
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('org_setup.sql') as f:
        db.cursor.executescript(f.read().decode('utf8'))
    db.commit()


@click.command()
def init_db_C():
    #init_db()
    click.echo('Initialized the database.')