from flask import Flask
from flask_cors import CORS

from api.item import item_api
from api.category import category_api
from api.catalog import catalog_api
from api.user_auth import user_auth_api


app = Flask(__name__)
CORS(app)

app.register_blueprint(item_api)
app.register_blueprint(category_api)
app.register_blueprint(catalog_api)
app.register_blueprint(user_auth_api)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
