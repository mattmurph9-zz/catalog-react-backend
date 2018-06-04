from flask import Blueprint
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response

from database_setup import Category, Item
from assets import verify_jwt, create_message_response
from session import session


category_api = Blueprint('category_api', __name__)


@category_api.route('/catalog/<string:category_name>', methods=['GET'])
def get_category(category_name):
    items_in_cat = session.query(Item).filter_by(category_name=category_name).all()
    response = jsonify(items=[i.serialize for i in items_in_cat])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@category_api.route('/catalog/<string:category_name>/delete', methods=['DELETE'])
def delete_category(category_name):
    # Delete category
    user_jwt = request.headers.get('Authorization')
    if user_jwt == u"null" or not verify_jwt(user_jwt):
        create_message_response('Unauthorized access', 400)
    else:
        del_cat = session.query(Category).filter_by(name=category_name).one()
        session.delete(del_cat)
        session.commit()
        return create_message_response('Category successfully deleted!', 200)


@category_api.route('/catalog/', methods=['POST'])
def add_category():
    user_jwt = request.headers.get('Authorization')
    if user_jwt == u"null" or not verify_jwt(user_jwt):
        return create_message_response('Unauthorized access', 400)
    data = request.get_json()
    if 'name' not in data:
        return create_message_response('Invalid request', 400)
    name = data['name']
    # If name is empty return error
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
