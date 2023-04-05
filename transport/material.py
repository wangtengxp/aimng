from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import json
import time

bp = Blueprint('material', __name__,url_prefix='/material')
materialTypes = {
    'SANZI':'散籽',
    'BAOYI_SANZI':'包衣散籽',
    'ZHONG_YI_JI':'种衣剂',
    'NEIMO':'内膜',
    'OUTER_PACK':'外包装',
    'CHENGPIN':'成品'
}
@bp.route('/list')
def index():
    db = get_db()
    materials = db.execute(
        'SELECT id, name, count,comment,type,unit,tag'
        ' FROM material'
        ' ORDER BY id DESC'
    ).fetchall()
    suppliers = db.execute('SELECT id,name from supplier order by id DESC').fetchall()
    return render_template('material/list.html', materials=materials,suppliers=suppliers)

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
        row={"id":int(id),"name":name,"count":float(count)}
        rows.append(row)
    return json.dumps(rows)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        count = request.form['count']
        unit = request.form['unit']
        comment = request.form['comment']
        type = request.form['type']
        tag = request.form['tag']

        error = None

        if not name:
            error = '请填写商品名称.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO material (name, count,unit,comment,type,tag,create_time)'
                ' VALUES (?, ?,?,?,?,?,?)',
                (name, count,unit,comment,type,tag,time.strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()
            return redirect(url_for('material.index'))

    return render_template('material/create.html',materialTypes=materialTypes,material={})

@bp.route('/<int:id>/modify', methods=('GET', 'POST'))
@login_required
def modifyMaterial(id):
    if request.method == 'POST':
        name = request.form['name']
        count = request.form['count']
        unit = request.form['unit']
        comment = request.form['comment']
        type = request.form['type']
        tag = request.form['tag']

        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE material set name=?,unit=?,comment=?,type=?,tag=?,count=? where id=?', (name,unit,comment,type,tag,count, id))
            db.commit()
        return redirect(url_for('material.index'))
    db = get_db()
    material = db.execute('select * from material where id=?',(id,)).fetchone()
    return render_template('material/create.html',materialTypes=materialTypes,material=material)

@bp.route('/importMaterial', methods=('GET', 'POST'))
@login_required
def importMaterial():
    #原材料进货
    if request.method == 'POST':
        materialId = request.form['materialId']
        # 进货量
        count = float(request.form['count'])
        #金额
        amount = request.form['amount']
        supplierId = request.form['supplierId']


        error = None
        if not amount:
            error = '请填写数量'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            originCountRow = db.execute('select count from material where id=?',(materialId,)).fetchone()
            newCount = float(originCountRow['count'])+count
            db.execute('UPDATE material set count=? where id=?', (newCount, materialId))

            db.execute('insert into supplier_accounts (supplier_id,entity_type,entity_id,amount_type,amount,create_time,count)'
                       'values (?,?,?,?,?,?,?)',(supplierId,'MATERIAL',materialId,'IMPORT_MATERIAL',amount,time.strftime('%Y-%m-%d %H:%M:%S'),count))
            db.commit()
    return redirect(url_for('material.index'))