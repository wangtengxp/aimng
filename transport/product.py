from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import json
import time

bp = Blueprint('product', __name__,url_prefix='/product')

@bp.route('/list')
def index():
    db = get_db()
    products = db.execute(
        'SELECT id, name, unit, specification, price,creator,material_cost_conf,comment,inventory'
        ' FROM product_def'
        ' ORDER BY id DESC'
    ).fetchall()

    materials = db.execute(
        'SELECT id, name, count'
        ' FROM material'
        ' ORDER BY id DESC'
    ).fetchall()

    if products is None or materials is None:
        return render_template('product/list.html', products=products)

    materialMap = dict()
    if materials is not None:
        for material in materials:
            materialMap[material['id']] = material['name']

    productList = []
    for product in products:
        productDict=dict(product)

        materialCostConfStr = product['material_cost_conf']
        materialCostStr = ""
        if materialCostConfStr is not None:
            materialCostConf = json.loads(materialCostConfStr)
            for cost in materialCostConf:
                materialCostStr+=materialMap.get(int(cost['materialId']))+":"+cost['materialCost']+";"
        productDict['material_cost_conf']=materialCostStr
        productList.append(productDict)


    return render_template('product/list.html', products=productList)

@bp.route('/findById/<int:id>', methods=('GET', 'POST'))
@login_required
def findById(id):
    db = get_db()
    product = db.execute('SELECT * from product_def where id=?',(id,)).fetchone()
    productDict = dict(product)
    materialCostConfStr = product['material_cost_conf']
    if materialCostConfStr is not None:
        materialCostConf = json.loads(materialCostConfStr)
        productDict['material_cost_conf'] = materialCostConf
    return json.dumps(productDict)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        unit = request.form['unit']
        price = request.form['price']
        comment = request.form['comment']
        specification = request.form['specification']
        formDict = dict(request.form.lists())
        material =formDict.get('material')
        materialCost = formDict.get('materialCost')
        

        error = None

        if not name:
            error = '请填写商品名称.'
        if not unit:
            error = '请填写单位'
        if not material:
            error = '没有获取到material'

        if error is not None:
            flash(error)
        else:
            materialCostArray = list()
            for i in range(len(material)):
                costDict=dict()
                costDict['materialId']=int(material[i])
                costDict['materialCost']=materialCost[i]
                materialCostArray.append(costDict)
            materialCostJson=json.dumps(materialCostArray)
            db = get_db()
            db.execute(
                'INSERT INTO product_def (name, unit, specification,price,creator,material_cost_conf,comment,create_time)'
                ' VALUES (?, ?, ?, ?, ?,?,?,?)',
                (name, unit, specification,price, g.user['username'],materialCostJson,comment,time.strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()
            return redirect(url_for('product.index'))

    return render_template('product/create.html',product={})
@bp.route('/<int:id>/modify', methods=('GET', 'POST'))
@login_required
def modify(id):
    if request.method == 'POST':
        id= request.form['id']
        name = request.form['name']
        unit = request.form['unit']
        price = request.form['price']
        comment = request.form['comment']
        specification = request.form['specification']
        formDict = dict(request.form.lists())
        material =formDict.get('material')
        materialCost = formDict.get('materialCost')

        error = None

        if not name:
            error = '请填写商品名称.'
        if not unit:
            error = '请填写单位'
        if not material:
            error = '没有获取到material'

        if error is not None:
            flash(error)
        else:
            materialCostArray = list()
            for i in range(len(material)):
                costDict=dict()
                costDict['materialId']=int(material[i])
                costDict['materialCost']=materialCost[i]
                materialCostArray.append(costDict)
            materialCostJson=json.dumps(materialCostArray)
            db = get_db()
            db.execute(
                'update product_def set name=?, unit=?, specification=?,price=?,material_cost_conf=?,comment=? '
                'where id = ?',
                (name, unit, specification,price,materialCostJson,comment,id)
            )
            db.commit()
            return redirect(url_for('product.index'))

    db = get_db()
    product = db.execute(
        'SELECT id, name, unit, specification, price,creator,material_cost_conf,comment'
        ' FROM product_def where id =?',(id,)
    ).fetchone()

    materials = db.execute(
        'SELECT id, name, count'
        ' FROM material'
        ' ORDER BY id DESC'
    ).fetchall()
    productDict = dict(product)
    materialCostConfStr = product['material_cost_conf']
    if materialCostConfStr is not None:
        materialCostConf = json.loads(materialCostConfStr)
        productDict['material_cost_conf'] = materialCostConf
    return render_template('product/create.html',product=productDict,materials=materials)
@bp.route('/manufacture', methods=('GET', 'POST'))
@login_required
def manufacture():
    if request.method == 'POST':
        productId = request.form['product']
        amount = float(request.form['amount'])

        formDict = dict(request.form.lists())
        material = formDict.get('material')
        materialCostProd = formDict.get('materialCost')

        error = None

        if not productId:
            error = '请选择商品.'
        if not amount:
            error = '请填写生产数量'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            materialCostArray = list()
            for i in range(len(material)):
                costDict = dict()
                costDict['materialId'] = int(material[i])
                costDict['materialCost'] = float(materialCostProd[i])
                materialCostArray.append(costDict)
            materialCostJson = json.dumps(materialCostArray)

            db.execute(
                'INSERT INTO manufacture_record (product_id, amount,create_time,material_cost)'
                ' VALUES (?, ?,?,?)',
                (productId, amount,time.strftime('%Y-%m-%d %H:%M:%S'),materialCostJson)
            )

            # materialCostRow = db.execute('select material_cost_conf from product_def where id=?',(productId,)).fetchone()
            # materialCostConf = json.loads(materialCostRow['material_cost_conf'])
            # for materialCost in materialCostConf:
            for i in range(len(material)):
                materialId=int(material[i])
                materialCost = float(materialCostProd[i])
                materialAmount = db.execute('select name,count from material where id=?',(materialId,)).fetchone()
                materialLeft = float(materialAmount['count'])-materialCost*amount
                db.execute('UPDATE material set count=? where id=?',(materialLeft,materialId))
            product = db.execute('select * from product_def where id=?',(productId,)).fetchone()

            newInventory = amount+product['inventory']
            db.execute('UPDATE product_def set inventory=? where id=?',(newInventory,productId))
            db.commit()
            return redirect(url_for('product.index'))
    db = get_db()
    products = db.execute(
        'SELECT id, name, unit, specification, price,creator,material_cost_conf'
        ' FROM product_def'
        ' ORDER BY id DESC'
    ).fetchall()

    materials = db.execute(
        'SELECT id, name, count'
        ' FROM material'
        ' ORDER BY id DESC'
    ).fetchall()

    return render_template('product/manufacture.html', products=products,materials=materials)

@bp.route('/delete', methods=('POST',))
@login_required
def delete():
    id = request.form['id']
    db = get_db()
    db.execute('DELETE FROM product_def WHERE id = ?', (id,))
    db.commit()
    # return
    return redirect(url_for('product.index'))