import httplib2
import json
import jwt

from flask import Blueprint
from flask import request
from flask import make_response
from sqlalchemy.orm.exc import NoResultFound

from session import session
from database_setup import User, verify_user


user_auth_api = Blueprint('user_auth_api', __name__)

SECRET = 'matt'
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


@user_auth_api.route('/reactconnect', methods=['POST'])
def reactconnect():
    data = request.get_json()
    access_token = data['access_token']
    # If access token not sent in request, return error response
    if not access_token:
        response = make_response(json.dumps('No access token present'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = data['token_id']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get user info
    email = data['email']
    user_id = get_user_id(email)
    if not user_id:
        input_dict = {'name': data['name'], 'email': data['email'], 'picture': data['picture']}
        user = verify_user(input_dict)
        session.add(user.data)
        session.commit()

    # Make JWT with users username
    user_jwt = jwt.encode({'username': email}, SECRET, algorithm='HS256')
    data = {'jwt': user_jwt}
    response = make_response(json.dumps(data), 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@user_auth_api.route('/reactdisconnect', methods=['POST'])
def reactdisconnect():
    data = request.get_json()
    access_token = data['access_token']
    # If no access_token, no user is connected
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Call to google to revoke token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.uid
    except NoResultFound:
        return None
