from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import json

bp = Blueprint('material', __name__,url_prefix='/material')

@bp.route('/list')
def index():
    db = get_db()
    materials = db.execute(
        'SELECT id, name, count'
        ' FROM material'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('material/list.html', materials=materials)

@bp.route('/getMaterials' , methods=('GET', 'POST'))
def material():
    db = get_db()
    materials = db.execute(
        'SELECT id, name, count'
        ' FROM material'
        ' ORDER BY id DESC'
    ).fetchall()
    rows=[]
    for(id,name,count) in materials:
        row={"id":int(id),"name":name,"count":int(count)}
        rows.append(row)
    return json.dumps(rows)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        count = request.form['count']

        error = None

        if not name:
            error = '请填写商品名称.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO material (name, count)'
                ' VALUES (?, ?)',
                (name, count)
            )
            db.commit()
            return redirect(url_for('material.index'))

    return render_template('material/create.html')

@bp.route('/modify', methods=('GET', 'POST'))
@login_required
def modifyMaterial():
    if request.method == 'POST':
        id = request.form['id']
        amount = request.form['amount']

        error = None
        if not amount:
            error = '请填写数量'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE material set count=? where id=?', (amount, id))
            db.commit()
    return redirect(url_for('material.index'))