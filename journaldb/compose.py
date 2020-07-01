# compose.py

import functools

from flask import (Blueprint, flash, g, render_template, request, url_for)

from journaldb.db import get_db

bp = Blueprint('compose', __name__, url_prefix='/compose')

@bp.route('/compose', methods=('GET', 'POST'))
def compose():
    if request.method == 'POST':
        date = request.form['date']
        body = request.form['body']
        db = get_db()
        error = None

        if not date:
            error = 'Date is required.'
        elif not body:
            error = 'Body cannot be empty.'
        elif db.execute('SELECT body FROM journal WHERE date = ?', (date,)).fetchone() is not None:
            error = 'Date {} is already recorded.'.format(date)

        if error is None:
            db.execute('INSERT INTO journal (date, body) VALUES (?, ?)', (date, body))
            db.commit()
            return redirect(url_for('hello'))

        flash(error)

    return render_template('compose/compose.html')
