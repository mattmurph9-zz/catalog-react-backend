from flask import Blueprint
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response

from database_setup import Category, Item
from session import session


catalog_api = Blueprint('catalog_api', __name__)

# Operations on the Catalog
# 1. Get list of categories
# 2. Get list of latest 10 items


# 1. Get list of categories
@catalog_api.route('/catalog/', methods=['GET'])
def category_list():
    # Get list of categories
    cat_list = session.query(Category).all()
    response = jsonify(categories=[cat.serialize for cat in cat_list])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# 2. Get list of latest 10 items
@catalog_api.route('/catalog/latest', methods=['GET'])
def latest():
    # Get latest 10 items
    latest_items = session.query(Item).order_by(Item.date.desc()).limit(10)
    response = jsonify(items=[i.serialize for i in latest_items])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
