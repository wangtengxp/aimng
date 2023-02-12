from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from transport.auth import login_required
from transport.db import get_db
import json

bp = Blueprint('customer', __name__,url_prefix='/customer')

@bp.route('/list')
def index():
    db = get_db()
    customers = db.execute(
        'SELECT id, name, cellphone,city,province,address'
        ' FROM customer'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('customer/list.html', customers=customers)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        cellphone = request.form['cellphone']
        city = request.form['city']
        province = request.form['province']
        address = request.form['address']


        error = None

        if not name:
            error = '请填写客户名称.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO customer (name, cellphone,city,province,address)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, cellphone,city,province,address)
            )
            db.commit()
            return redirect(url_for('customer.index'))

    return render_template('customer/create.html')