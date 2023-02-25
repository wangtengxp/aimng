from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .auth import login_required
from .db import get_db
import json
import os

UPLOAD_FOLDER = 'D:/github/aimng/transport/path/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

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
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            return {
              "code": 0
              ,"msg": ""
              ,"data": {
                "src": url_for('carriage.uploaded_file',
                    filename=filename)
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
    # sellRecords = db.execute('select id from sell_record order by id desc').fetchall()

    sellRecords = db.execute(
        'SELECT sr.id, sr.create_time, sr.amount,pd.name as product_name,sl.name as seller_name,cst.name as customer_name,sr.transported_amount as transported_amount'
        ' FROM sell_record sr left join product_def pd on sr.product_id=pd.id left join seller sl on sr.seller_id= sl.id left join customer cst on sr.customer_id=cst.id'
        ' ORDER BY sr.id DESC'
    ).fetchall()

    return render_template('carriage/create.html',sellRecords=sellRecords)

