from flask import Blueprint
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response

from database_setup import Category, Item
from assets import verify_jwt, create_message_response
from session import session


category_api = Blueprint('category_api', __name__)

# Operations on a Category
# 1. Get list of items in category
# 2. Delete a category
# 3. Add a new category


# 1. Get list of items in category
@category_api.route('/catalog/<string:category_name>', methods=['GET'])
def get_category(category_name):
    items_in_cat = session.query(Item).filter_by(category_name=category_name).all()
    response = jsonify(items=[i.serialize for i in items_in_cat])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# 2. Delete a category
@category_api.route('/catalog/<string:category_name>/delete', methods=['DELETE'])
def delete_category(category_name):
    user_jwt = request.headers.get('Authorization')
    # If user is not logged in or user is not in db return error response
    if user_jwt == u"null" or not verify_jwt(user_jwt):
        create_message_response('Unauthorized access', 400)
    else:
        del_cat = session.query(Category).filter_by(name=category_name).one()
        session.delete(del_cat)
        session.commit()
        return create_message_response('Category successfully deleted!', 200)


# 3. Add a new category
@category_api.route('/catalog/', methods=['POST'])
def add_category():
    user_jwt = request.headers.get('Authorization')
    # If user is not logged in or user is not in db return error response
    if user_jwt == u"null" or not verify_jwt(user_jwt):
        return create_message_response('Unauthorized access', 400)
    data = request.get_json()
    # Check if request has required content
    if 'name' not in data:
        return create_message_response('Invalid request', 400)
    name = data['name']
    # If name is empty or whitespace return error
    if name.isspace() or not name:
        return create_message_response('Name cannot be empty', 400)
    else:
        # If name already exists in Category table return error
        category_exists = session.query(Category).filter_by(name=name).all()
        if category_exists:
            return create_message_response('Category already exists', 400)
        else:
            new_category = Category(name=name)
            session.add(new_category)
            session.commit()
            return create_message_response('Category successfully added!', 200)
