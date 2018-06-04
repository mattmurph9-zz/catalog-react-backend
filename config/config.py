import json
from urllib import quote_plus as urlquote
with open('config/config.json', 'r') as f:
    config = json.load(f)

mysql = config['mysql']
mysql['password'] = urlquote(mysql['password'])
engine_str = (
    "mysql+pymysql://{user_name}:{password}@{host}:3306/{database_name}"
    .format(**mysql))
