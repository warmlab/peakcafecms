import hashlib
import json
from decimal import Decimal
from datetime import datetime

from flask import render_template, abort
from flask import request, current_app, make_response, url_for

from . import home
from .. import db

from ..models import ProductCategory, ProductTag, Product

@home.route('/search', methods=['POST'])
def search():
    key = request.form.get('search')
    names = Product.query.filter(Product.name.like('%{}%'.format(key)))
    ids = []
    herbals = []
    for name in names:
        if name.herbal_id not in ids:
            name.herbal.name = name.name
            herbals.append(name.herbal)
            ids.append(name.herbal_id)
    return render_template('home/result.html', herbs=herbals)

@home.route('/menu', methods=['GET'])
@home.route('/menu/<code>', methods=['GET'])
def menu(code='8461786b752549cc8cd2b2977a54dac6'):
    if not code:
        category = ProductCategory.query.first_or_404()
    else:
        category = ProductCategory.query.filter_by(code=code).first_or_404()
    categories = ProductCategory.query.all()

    products = [] #category.products
    
    return render_template('home/menu.html', categories=categories, category=category)

@home.route('/', methods=['GET'])
def home():
    return render_template('home/index.html')
