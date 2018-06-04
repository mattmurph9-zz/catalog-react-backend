import jwt

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, make_response

from database_setup import User
from session import session


SECRET = 'matt'

# Take jwt input, decode and check if user exists in db
def verify_jwt(user_jwt):
    user_info = jwt.decode(user_jwt, SECRET, algorithms=['HS256'])
    username = user_info['username']
    user = session.query(User).filter_by(email=username)
    if not user:
        return False
    else:
        return True


def create_message_response(message, status):
    data = {'message': message}
    response = make_response(jsonify(data), status)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def create_data_response(data):
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
