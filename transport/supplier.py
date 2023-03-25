from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required
from .db import get_db
import time

bp = Blueprint('supplier', __name__,url_prefix='/supplier')

@bp.route('/list')
def index():
    db = get_db()
    suppliers = db.execute(
        'SELECT id, name, cellphone,contacts,paid'
        ' FROM supplier'
        ' ORDER BY id desc'
    ).fetchall()
    return render_template('supplier/list.html', suppliers=suppliers)
@bp.route('/detail/<int:supplierId>', methods=('GET', 'POST'))
@login_required
def accountsDetail(supplierId):
    db = get_db()
    accounts = db.execute('select spl_acc.id,spl_acc.amount,spl_acc.amount_type,spl_acc.create_time,spl_acc.count,spl.name m.name as material_name,m.unit as material_unit from supplier_accounts spl_acc'
                          ' left join supplier spl on spl_acc.supplier_id=spl.id left join material m on spl_acc.entity_id=m.id and spl_acc.entity_type="MATERIAL" where supplier_id=?',(supplierId,)).fetchall()
    return render_template('supplier/detail.html',accounts=accounts)

@bp.route('/printDetail/<int:accountsId>', methods=('GET', 'POST'))
@login_required
def printDetail(accountsId):
    db = get_db()
    account = db.execute('select spl_acc.amount,spl_acc.amount_type,spl_acc.create_time,cst.name from supplier_accounts spl_acc'
                          ' left join supplier spl on spl_acc.supplier_id=spl.id where spl_acc.id=?',(accountsId,)).fetchone()
    return render_template('supplier/printDetail.html',account=account)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        cellphone = request.form['cellphone']
        contacts = request.form['contacts']

        error = None

        if not name:
            error = '请填写客户名称.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO supplier (name, cellphone,contacts,create_time)'
                ' VALUES (?, ?, ?, ?)',
                (name, cellphone,contacts,time.strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()
            return redirect(url_for('supplier.index'))

    return render_template('supplier/create.html')

# @bp.route('/receiveMoney', methods=('GET', 'POST'))
# @login_required
# def receiveMoney():
#     id = request.form['id']
#     print('receiveMoney:%s', id)
#     money = float(request.form['money'])
#     print('receiveMoney:%s', money)
#
#     error = None
#     if not money:
#         error = '请填写金额'
#
#     if error is not None:
#         flash(error)
#     else:
#         db = get_db()
#         #新建账务明细
#         db.execute('insert into customer_accounts (customer_id,entity_type,entity_id,amount,amount_type,create_time)'
#                    ' VALUES (?,?,?,?,?,?)',(id,'CUSTOMER',id,money,'PAYMENT',time.strftime('%Y-%m-%d %H:%M:%S')))
#         customerRow = db.execute('SELECT receivable from customer where id= ?', (id,)).fetchone()
#         receivable = float(customerRow['receivable'])
#         db.execute('UPDATE customer set receivable=? where id=?', (receivable-money, id))
#         db.commit()
#     return redirect(url_for('customer.index'))