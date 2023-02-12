from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from transport.auth import login_required
from transport.db import get_db
import json

bp = Blueprint('seller', __name__,url_prefix='/seller')

@bp.route('/list')
def index():
    db = get_db()
    sellers = db.execute(
        'SELECT id, name, cellphone'
        ' FROM seller'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('seller/list.html', sellers=sellers)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        cellphone = request.form['cellphone']

        error = None

        if not name:
            error = '请填写客户名称.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO seller (name, cellphone)'
                ' VALUES (?, ?)',
                (name, cellphone)
            )
            db.commit()
            return redirect(url_for('seller.index'))

    return render_template('seller/create.html')