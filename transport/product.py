from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import json

bp = Blueprint('product', __name__,url_prefix='/product')

@bp.route('/list')
def index():
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
        materialCostConf = json.loads(materialCostConfStr)
        materialCostStr=""
        for cost in materialCostConf:
            materialCostStr+=materialMap.get(int(cost['materialId']))+":"+cost['materialCost']+";"
        productDict['material_cost_conf']=materialCostStr
        productList.append(productDict)


    return render_template('product/list.html', products=productList)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        unit = request.form['unit']
        price = request.form['price']
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
                costDict['materialId']=material[i]
                costDict['materialCost']=materialCost[i]
                materialCostArray.append(costDict)
            materialCostJson=json.dumps(materialCostArray)
            db = get_db()
            db.execute(
                'INSERT INTO product_def (name, unit, specification,price,creator,material_cost_conf)'
                ' VALUES (?, ?, ?, ?, ?,?)',
                (name, unit, specification,price, g.user['username'],materialCostJson)
            )
            db.commit()
            return redirect(url_for('product.index'))

    return render_template('product/create.html')

@bp.route('/manufacture', methods=('GET', 'POST'))
@login_required
def manufacture():
    if request.method == 'POST':
        productId = request.form['product']
        amount = float(request.form['amount'])

        error = None

        if not productId:
            error = '请选择商品.'
        if not amount:
            error = '请填写生产数量'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO manufacture_record (product_id, amount)'
                ' VALUES (?, ?)',
                (productId, amount)
            )

            materialCostRow = db.execute('select material_cost_conf from product_def where id=?',(productId,)).fetchone()
            materialCostConf = json.loads(materialCostRow['material_cost_conf'])
            for materialCost in materialCostConf:
                materialId=int(materialCost['materialId'])
                materialCost = int(materialCost['materialCost'])
                materialAmount = db.execute('select name,count from material where id=?',(materialId,)).fetchone()
                materialLeft = int(materialAmount['count'])-materialCost*amount
                if(materialLeft<0):
                    flash("原材料'"+str(materialAmount['name'])+"'不足")
                    return redirect(url_for('product.index'))
                db.execute('UPDATE material set count=? where id=?',(materialLeft,materialId))
            inventory = db.execute('select * from product_inventory where product_id=?',(productId,)).fetchone()

            if inventory is None:
                db.execute('INSERT INTO product_inventory (product_id, amount)'
                ' VALUES (?, ?)',
                (productId, amount))

            else:
                newAmount = amount+inventory['amount']
                db.execute('UPDATE product_inventory set amount=? where id=?',(newAmount,inventory['id']))
            db.commit()
            return redirect(url_for('product.index'))
    db = get_db()
    products = db.execute(
        'SELECT id, name, unit, specification, price,creator,material_cost_conf'
        ' FROM product_def'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('product/manufacture.html', products=products)
#
# def get_post(id, check_author=True):
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()
#
#     if post is None:
#         abort(404, "Post id {0} doesn't exist.".format(id))
#
#     if check_author and post['author_id'] != g.user['id']:
#         abort(403)
#
#     return post
#
# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)
#
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None
#
#         if not title:
#             error = 'Title is required.'
#
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE post SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))
#
#     return render_template('blog/update.html', post=post)
#
@bp.route('/delete', methods=('POST',))
@login_required
def delete():
    id = request.form['id']
    db = get_db()
    db.execute('DELETE FROM product_def WHERE id = ?', (id,))
    db.commit()
    # return
    return redirect(url_for('product.index'))