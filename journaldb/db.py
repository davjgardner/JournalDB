# db.py

import sqlite3

import re
import datetime
import calendar

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'],
                               detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(import_data_command)

@click.command('import')
@click.argument('datafile')
@with_appcontext
def import_data_command(datafile):
    # Match the form '7/1/2020 - Wednesday' -> (7, 1, 2020, ( - Wednesday)?, Wednesday)
    r = re.compile(r'(\d{1,2})\/(\d{1,2})\/(\d{2,4})(\s*-\s*(\w+))?')
    with open(datafile) as f:
        prev_date = None
        curr_date = None
        weekday = None
        entry_added = True
        db = get_db()
        #l = f.readlines()
        lnum = -1
        error = False
        for line in f:
            lnum += 1
            line = line.rstrip()
            if line == '':
                continue
            # is this a date line?
            d = r.match(line)
            # if so set current date, compare against prev
            if d:
                error = False
                # apparently group(0) is the full match
                month = int(d.group(1))
                day = int(d.group(2))
                year = int(d.group(3))
                if year < 100: year += 2000
                weekday = d.group(5)
                prev_date = curr_date
                curr_date = datetime.date(year, month, day)
                if not entry_added:
                    click.echo('[{}] WARNING: no entry added for date {}'.format(lnum, prev_date))
                if prev_date:
                    oneday = datetime.timedelta(days=1)
                    if curr_date - prev_date == datetime.timedelta(0):
                        click.echo('[{}] DUPLICATE!! {}'.format(lnum, curr_date))
                    elif curr_date - prev_date != oneday:
                        click.echo('[{}] SKIP!! {} -> {}'.format(lnum, prev_date, curr_date))
                        # Did I just type the year wrong?
                        if curr_date.year != prev_date.year:
                            curr_date = datetime.date(prev_date.year, curr_date.month, curr_date.day)
                            if curr_date - prev_date != oneday:
                                click.echo('[{}] nope, still wrong'.format(lnum))
                if weekday:
                    if weekday != calendar.day_name[curr_date.weekday()]:
                        click.echo('[{}] WRONG DAY NAME!! Expected "{}", got "{}" for {}'
                                   .format(lnum,calendar.day_name[curr_date.weekday()], weekday, curr_date))
                        weekday = calendar.day_name[curr_date.weekday()]
                entry_added = False

            else:
                # if not, add to db under current date
                if error:
                    click.echo('-> Skipping the following entry:')
                    click.echo(line)
                else:
                    e = db.execute('SELECT id, body FROM journal WHERE date = ?', (curr_date,)).fetchone()
                    if e:
                        click.echo('WARNING: An entry for {} already exists, appending this one'.format(curr_date))
                        db.execute('UPDATE JOURNAL SET body = ? WHERE date = ?', (e['body'] + '\n' + line, curr_date))
                        db.commit()
                    else:
                        db.execute('INSERT INTO journal (date, weekday, body) VALUES (?, ?, ?)', (curr_date, weekday, line))
                        db.commit()
                    entry_added = True
