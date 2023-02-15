from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db
import json

bp = Blueprint('carriage', __name__,url_prefix='/carriage')

@bp.route('/list')
def index():
    db = get_db()
    transports = db.execute(
        'SELECT id,sell_record_id, amount, address,driver_name,driver_cellphone'
        ' FROM transport'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('carriage/list.html', transports=transports)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        sell_record_id = request.form['sell_record_id']
        amount = request.form['amount']
        address = request.form['address']
        driver_name = request.form['driver_name']
        driver_cellphone = request.form['driver_cellphone']

        error = None

        if not sell_record_id:
            error = '请选择销售订单.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO transport (sell_record_id, amount, address,driver_name,driver_cellphone)'
                ' VALUES (?, ?, ?, ?, ?)',
                (sell_record_id, amount, address,driver_name,driver_cellphone)
            )
            #更新销售订单已发货数量
            transportedAmount = float(sellRecordRow['transported_amount'])
            newTransportedAmount =transportedAmount+float(amount)
            sellAmount=float(sellRecordRow['amount'])
            if newTransportedAmount>sellAmount:
                flash('发货总量超过了销售数量，请确认')
                return redirect(url_for('carriage.index'))

            db.execute('update sell_record set transported_amount=? where id=?',(newTransportedAmount,sell_record_id))
            db.commit()
            return redirect(url_for('carriage.index'))
    db = get_db()
    sellRecords = db.execute('select id from sell_record order by id desc').fetchall()
    return render_template('carriage/create.html',sellRecords=sellRecords)