## Requirements
- Python
- virtualenv
- MySQL

## Installation
- Clone this repository

## Environment Setup
- cd to cloned repository
- Setup and start virtual environment
```
virtualenv venv
. venv/bin/activate
```
- Install requirements
```
pip install -r req.txt
pip install PyJWT --upgrade
```

## Configure MySQL
- open mysql session:
```
mysql -u root -p
```
- Create database for project
```
CREATE DATABASE catalog;
```
- Grant permissions to user
```
GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost' IDENTIFIED BY 'password';
```
- Fill in username and password of the MySQL user you are using
- Open config/config.json file and change user_name and password fields

## To Run...
```
python projectreact.py
```