# notes.py

import functools

import datetime
import calendar

from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)

from journaldb.db import get_db

bp = Blueprint('notes', __name__)

def add_entry(date, body):
    db = get_db()
    error = None

    if not date:
        error = 'Date is required.'
    elif not body:
        error = 'Entry cannot be empty.'
    else:
        e = db.execute('SELECT id FROM journal WHERE date = ?', (date,)).fetchone()
        if e is not None:
            error = 'Date {} is already recorded. Edit?'.format(date)
            flash (error)
            # TODO: save typed body text, show it in the edit screen
            return redirect(url_for('notes.edit', id=e['id']))

    if error is None:
        weekday = calendar.day_name[datetime.date.fromisoformat(date).weekday()]
        db.execute('INSERT INTO journal (date, weekday, body) VALUES (?, ?, ?)', (date, weekday, body))
        db.commit()
        return redirect(url_for('notes.index'))

    flash(error)

    return render_template('compose.html')


@bp.route('/compose', methods=('GET', 'POST'))
def compose():
    if request.method == 'POST':
        date = request.form['date']
        body = request.form['body']
        return add_entry(date, body)

@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    if request.method == 'POST':
        date = request.form['date']
        body = request.form['body']
        return add_entry(date, body)

    entries = db.execute('SELECT id, date, weekday, body FROM journal ORDER BY date DESC').fetchall()
    return render_template('view.html', entries=entries, date=datetime.date.today())

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    db = get_db()
    entry = db.execute('SELECT id, date, body FROM journal WHERE id = ?', (id,)).fetchone()

    if entry is None:
        abort(404, "Could not find the requested entry (id = {0}).".format(id))

    if request.method == 'POST':
        date = request.form['date']
        body = request.form['body']
        error = None

        if not date:
            error = 'Date is required.'
        elif not body:
            error = 'Entry cannot be empty.'

        if error is None:
            weekday = weekday = calendar.day_name[datetime.date.fromisoformat(date).weekday()]
            db.execute('UPDATE journal SET date = ?, weekday = ?, body = ? WHERE id = ?', (date, weekday, body, id))
            db.commit()
            return redirect(url_for('notes.index'))

    return render_template('edit.html', entry=entry)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    db = get_db()
    entry = db.execute('SELECT id, date, body FROM journal WHERE id = ?', (id,)).fetchone()
    db.execute('DELETE FROM journal WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('notes.index'))
