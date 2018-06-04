import jwt

from flask import Blueprint
from flask import request, jsonify

from assets import verify_jwt, create_message_response
from database_setup import Item, verify_item
from session import session

item_api = Blueprint('item_api', __name__)

SECRET = 'matt'


@item_api.route('/catalog/<string:category_name>/<string:item_name>', methods=['GET'])
def get_item(category_name, item_name):
    # Get item information
    item = session.query(Item).filter_by(name=item_name).one()
    response = jsonify(item=item.serialize)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@item_api.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['DELETE'])
def delete_item(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    user_jwt = request.headers.get('Authorization')
    if user_jwt == u"null" or not verify_jwt(user_jwt):
        return create_message_response('Unauthorized access', 400)
    else:
        user_info = jwt.decode(user_jwt, SECRET, algorithms=['HS256'])
        if user_info['username'] == item.creator:
            session.delete(item)
            session.commit()
            return create_message_response('Item successfully deleted', 200)
        else:
            return create_message_response('Unauthorized access', 400)


@item_api.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['PUT'])
def edit_item(category_name, item_name):
    data = request.get_json()
    item = session.query(Item).filter_by(name=item_name).one()
    user_jwt = request.headers.get('Authorization')
    if user_jwt == u"null" or not verify_jwt(user_jwt):
        return create_message_response('Unauthorized access', 400)
    else:
        user_info = jwt.decode(user_jwt, SECRET, algorithms=['HS256'])

        if 'name' not in data or 'description' not in data:
            return create_message_response('Invalid input', 400)
        if user_info['username'] == item.creator:
            input_dict = {'name': data['name'], 'description': data['description'],
                          'category_name': item.category_name, 'creator': item.creator, }
            item_mm = verify_item(input_dict)
            if item_mm.errors:
                return create_message_response('Input cannot be empty', 400)
            else:
                item.name = item_mm.data.name
                item.description = item_mm.data.description
                session.add(item)
                session.commit()
                return create_message_response('Item successfully edited', 200)
        else:
            return create_message_response('Unauthorized access', 400)


@item_api.route('/catalog/<string:category_name>', methods=['POST'])
def add_item(category_name):
    user_jwt = request.headers.get('Authorization')
    # If user is not logged in or user is not in db
    if user_jwt == u"null" or not verify_jwt(user_jwt):
        return create_message_response('Unauthorized access', 400)
    else:
        # Get creator username from jwt in authorization header
        user_info = jwt.decode(user_jwt, SECRET, algorithms=['HS256'])
        creator = user_info['username']
        data = request.get_json()
        name = data['name']
        desc = data['description']
        if not name or not desc:
            return create_message_response('Invalid input', 400)
        # Use Marshmallow to create item object
        input_dict = {'name': data['name'],
                      'description': data['description'],
                      'category_name': category_name,
                      'creator': creator}
        item_mm = verify_item(input_dict)
        # If errors exist in object, one of the input fields is empty
        if item_mm.errors:
            return create_message_response('input cannot be empty', 400)
        else:
            # Check if input item name already exists in db
            item_exists = session.query(Item).filter_by(name=data['name']).all()
            if item_exists:
                return create_message_response('Item already exists', 400)
            # If item doesn't already exist, create new item and add to db
            else:
                new_item = Item(name=name,
                                description=desc,
                                category_name=category_name,
                                creator=creator)
                session.add(new_item)
                session.commit()
                return create_message_response('Item successfully added!', 200)