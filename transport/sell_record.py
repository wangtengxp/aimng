from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db
import json

bp = Blueprint('sell_record', __name__,url_prefix='/sell_record')

@bp.route('/list')
def index():
    db = get_db()
    sellRecords = db.execute(
        'SELECT sr.id, sr.create_time, sr.amount,pd.name as product_name,sl.name as seller_name,cst.name as customer_name,sr.transported_amount as transported_amount'
        ' FROM sell_record sr left join product_def pd on sr.product_id=pd.id left join seller sl on sr.seller_id= sl.id left join customer cst on sr.customer_id=cst.id'
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

        error = None

        if not product_id:
            error = '请选择销售的产品'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # 查询产品库存
            inventoryRow = db.execute('select amount from product_inventory where product_id=?',
                                      (product_id,)).fetchone()
            inventoryAmount = float(inventoryRow['amount'])
            #产品库存允许为负数
            inventoryLeft = inventoryAmount - float(amount)
            # 更新产品库存
            db.execute('update product_inventory set amount=? where product_id=?', (inventoryLeft, product_id))

            #创建销售记录
            db.execute(
                'INSERT INTO sell_record (product_id, amount,seller_id,customer_id,status)'
                ' VALUES (?, ?, ?, ?, ?)',
                (product_id, amount,seller_id,customer_id,'INIT')
            )
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