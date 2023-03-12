from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required
from .db import get_db
import time

bp = Blueprint('customer', __name__,url_prefix='/customer')

@bp.route('/list')
def index():
    db = get_db()
    customers = db.execute(
        'SELECT id, name, cellphone,city,province,address,salesman,contacts,receivable'
        ' FROM customer'
        ' ORDER BY id'
    ).fetchall()
    return render_template('customer/list.html', customers=customers)
@bp.route('/detail/<int:customerId>', methods=('GET', 'POST'))
@login_required
def accountsDetail(customerId):
    db = get_db()
    if customerId>0:
        accounts = db.execute('select cus_acc.amount,cus_acc.amount_type,cus_acc.create_time,cst.name from customer_accounts cus_acc'
                              ' left join customer cst on cus_acc.customer_id=cst.id where customer_id=?',(customerId,)).fetchall()
        return render_template('customer/detail.html',accounts=accounts)
    accounts = db.execute(
        'select cus_acc.amount,cus_acc.amount_type,cus_acc.create_time,cst.name from customer_accounts cus_acc'
        ' left join customer cst on cus_acc.customer_id=cst.id').fetchall()
    return render_template('customer/detail.html',accounts=accounts)

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
                'INSERT INTO customer (name, cellphone,city,province,address,create_time)'
                ' VALUES (?, ?, ?, ?, ?,?)',
                (name, cellphone,city,province,address,time.strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()
            return redirect(url_for('customer.index'))

    return render_template('customer/create.html')

@bp.route('/receiveMoney', methods=('GET', 'POST'))
@login_required
def receiveMoney():
    id = request.form['id']
    print('receiveMoney:%s', id)
    money = float(request.form['money'])
    print('receiveMoney:%s', money)

    error = None
    if not money:
        error = '请填写金额'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        #新建账务明细
        db.execute('insert into customer_accounts (customer_id,entity_type,entity_id,amount,amount_type,create_time)'
                   ' VALUES (?,?,?,?,?,?)',(id,'CUSTOMER',id,money,'PAYMENT',time.strftime('%Y-%m-%d %H:%M:%S')))
        customerRow = db.execute('SELECT receivable from customer where id= ?', (id,)).fetchone()
        receivable = float(customerRow['receivable'])
        db.execute('UPDATE customer set receivable=? where id=?', (receivable-money, id))
        db.commit()
    return redirect(url_for('customer.index'))