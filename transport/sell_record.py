from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import time
import json

bp = Blueprint('sell_record', __name__,url_prefix='/sell_record')

@bp.route('/list')
def index():
    db = get_db()
    sellRecords = db.execute(
        'SELECT sr.id, sr.create_time, sr.amount,sr.return_money,sr.surrogate_fees,sr.status,pd.name as product_name,sl.name as seller_name,cst.name as customer_name,sr.transported_amount as transported_amount,cus_acc.amount as prepayments'
        ' FROM sell_record sr left join product_def pd on sr.product_id=pd.id left join seller sl on sr.seller_id= sl.id left join customer cst on sr.customer_id=cst.id'
        ' left join customer_accounts cus_acc on sr.id=cus_acc.entity_id and cus_acc.entity_type="SELL_RECORD"'
        ' ORDER BY sr.id DESC'
    ).fetchall()
    return render_template('sell_record/list.html', sellRecords=sellRecords)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        product_id = request.form['product_id']
        amount = request.form['amount']
        seller_id = request.form['seller_id']
        customer_id = request.form['customer_id']
        prepayments = float(request.form['prepayments'])

        error = None

        if not product_id:
            error = '请选择销售的产品'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # 查询产品库存
            productRow = db.execute('select inventory from product_def where id=?',
                                      (product_id,)).fetchone()
            inventoryAmount = float(productRow['inventory'])
            #产品库存允许为负数
            inventoryLeft = inventoryAmount - float(amount)
            # 更新产品库存
            db.execute('update product_def set inventory=? where id=?', (inventoryLeft, product_id))

            #创建销售记录
            sellRecordRow = db.execute(
                'INSERT INTO sell_record (product_id, amount,seller_id,customer_id,status,create_time)'
                ' VALUES (?, ?, ?, ?, ?,?)',
                (product_id, amount,seller_id,customer_id,'INIT',time.strftime('%Y-%m-%d %H:%M:%S'))
            )
            # 创建预付款
            if prepayments > 0.01:
                db.execute('INSERT INTO customer_accounts (customer_id,amount,entity_type,entity_id,amount_type,create_time)'
                           ' VALUES (?,?,?,?,?,?)',(customer_id,prepayments,'SELL_RECORD',sellRecordRow.lastrowid,'PREPAYMENTS',time.strftime('%Y-%m-%d %H:%M:%S')))
            db.commit()
            return redirect(url_for('sell_record.index'))

    db = get_db()
    products = db.execute('select id,name from product_def').fetchall()
    sellers = db.execute('select id,name from seller').fetchall()
    customers = db.execute('select id,name from customer').fetchall()

    sellCreateInfos = dict()
    sellCreateInfos['products']=products
    sellCreateInfos['sellers'] = sellers
    sellCreateInfos['customers'] = customers


    return render_template('sell_record/create.html',sellCreateInfos=sellCreateInfos)

@bp.route('/delete', methods=('POST',))
@login_required
def delete():
    id = request.form['id']
    db = get_db()
    db.execute('DELETE FROM sell_record WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('sell_record.index'))

@bp.route('/returnProduct', methods=('POST',))
@login_required
def returnProduct():
    id = request.form['sellRecordId']
    return_type = str(request.form['return_type'])
    return_money = request.form['return_money']
    surrogate_fees = request.form['surrogate_fees']

    db = get_db()
    if "returnProductAndMoney"==return_type:
        db.execute('update sell_record set return_money=?,status="RETURN_PRODUCT_MONEY" WHERE id = ?', (return_money, id))
    elif "surrogate"==return_type:
        db.execute('update sell_record set surrogate_fees=?,status="SURROGATE" WHERE id = ?', (surrogate_fees, id))
    db.commit()
    return redirect(url_for('sell_record.index'))