from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .auth import login_required
from .db import get_db
import json
import os
import uuid
import time

UPLOAD_FOLDER_RELATIVE='/static/uploads/driver_liscense/'
UPLOAD_FOLDER = 'D:/github/aimng/transport'+UPLOAD_FOLDER_RELATIVE
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

bp = Blueprint('carriage', __name__,url_prefix='/carriage')

@bp.route('/list')
def index():
    db = get_db()
    transports = db.execute(
        'SELECT tsp.id,tsp.sell_record_id, tsp.amount,tsp.product_price, tsp.address,tsp.driver_name,tsp.driver_cellphone,tsp.driver_liscense,tsp.create_time,'
        'prod_def.name as product_name'
        ' FROM transport tsp left join sell_record sr on tsp.sell_record_id=sr.id left join product_def prod_def on sr.product_id=prod_def.id'
        ' ORDER BY tsp.id DESC'
    ).fetchall()
    return render_template('carriage/list.html', transports=transports)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/uploadDriverLicense', methods=('GET', 'POST'))
@login_required
def uploadDriverLicense():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('文件没有内容')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('文件不存在')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = uuid.uuid1().__str__()+'.'+file.filename.split('.')[1]
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            return {
              "code": 0
              ,"msg": ""
              ,"data": {
                "src": UPLOAD_FOLDER_RELATIVE+filename
              }
            }
    return {
      "code": 0
      ,"msg": ""
      ,"data": {
        "src": "http://oss.layuion.com/123.jpg"
      }
    }

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER,
                               filename)
@bp.route('/printCarriage/<int:id>', methods=('GET', 'POST'))
@login_required
def printCarriage(id):
    db = get_db()
    transport = db.execute(
        'SELECT tsp.id,tsp.sell_record_id, tsp.amount,tsp.product_price, tsp.address,tsp.driver_name,tsp.driver_cellphone,tsp.driver_liscense,tsp.create_time,'
        'prod_def.name as product_name,prod_def.unit'
        ' FROM transport tsp left join sell_record sr on tsp.sell_record_id=sr.id left join product_def prod_def on sr.product_id=prod_def.id'
        ' WHERE tsp.id =?',(id,)
    ).fetchone()
    return render_template('carriage/printCarriage.html', transport=transport)
@bp.route('/create/<int:sellRecordId>', methods=('GET', 'POST'))
@login_required
def create(sellRecordId):
    if request.method == 'POST':
        sell_record_id = request.form['sell_record_id']
        #发货量
        amount = request.form['amount']
        #发货总金额
        productPrice = float(request.form['productPrice'])
        address = request.form['address']
        driver_name = request.form['driver_name']
        driver_cellphone = request.form['driver_cellphone']
        driver_liscense = request.form['driver_liscense']


        error = None

        if not sell_record_id:
            error = '请选择销售订单.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            #创建发货单
            db.execute(
                'INSERT INTO transport (sell_record_id, amount,product_price, address,driver_name,driver_cellphone,driver_liscense,create_time)'
                ' VALUES (?, ?, ?, ?, ?,?,?,?)',
                (sell_record_id, amount,productPrice, address,driver_name,driver_cellphone,driver_liscense,time.strftime('%Y-%m-%d %H:%M:%S'))
            )
            #更新销售订单已发货数量
            sellRecordRow = db.execute('SELECT transported_amount,amount,product_id,customer_id from sell_record where id= ?',(sell_record_id,)).fetchone()
            productId = int(sellRecordRow['product_id'])
            customerId = int(sellRecordRow['customer_id'])
            transportedAmount = float(sellRecordRow['transported_amount'])
            newTransportedAmount =transportedAmount+float(amount)
            sellAmount=float(sellRecordRow['amount'])
            if newTransportedAmount>sellAmount:
                flash('发货总量超过了销售数量，请确认')
                return redirect(url_for('carriage.index'))

            db.execute('update sell_record set transported_amount=? where id=?',(newTransportedAmount,sell_record_id))
            #减少库存
            # sellProduct = db.execute('SELECT inventory from product_def where id=?',(productId,)).fetchone()
            # productInventory = float(sellProduct['inventory'])
            # db.execute('UPDATE product_def set inventory=? where id=?',(productInventory-amount,productId))
            #增加客户应收
            customer = db.execute('SELECT receivable from customer where id=?',(customerId,)).fetchone()
            customerReceivable = float(customer['receivable'])
            db.execute('UPDATE customer set receivable=? where id=?',(customerReceivable+productPrice,customerId))
            db.commit()
            return redirect(url_for('carriage.index'))
    db = get_db()
    # sellRecords = db.execute('select id from sell_record order by id desc').fetchall()

    sellRecords = db.execute(
        'SELECT sr.id, sr.create_time, sr.amount,pd.name as product_name,sl.name as seller_name,cst.name as customer_name,sr.transported_amount as transported_amount'
        ' FROM sell_record sr left join product_def pd on sr.product_id=pd.id left join seller sl on sr.seller_id= sl.id left join customer cst on sr.customer_id=cst.id'
        ' ORDER BY sr.id DESC'
    ).fetchall()

    return render_template('carriage/create.html',sellRecords=sellRecords,sellRecordId=int(sellRecordId))

