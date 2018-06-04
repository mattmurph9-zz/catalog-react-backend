import datetime

from marshmallow import Schema, fields, pprint, post_load, ValidationError, validates
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from config.config import engine_str

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    name = Column(String(80), nullable=False)
    email = Column(String(80), primary_key=True)
    picture = Column(String(250), nullable=False)
    uid = Column(Integer, unique=True, nullable=False)


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), primary_key=True)
    item = relationship("Item", cascade="all,delete", backref="category")

    @property
    def serialize(self):
        return {
            'name': self.name,
        }


class Item(Base):
    __tablename__ = 'item'
    name = Column(String(80), primary_key=True)
    description = Column(String(250))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    category_name = Column(String(80), ForeignKey('category.name'))
    category1 = relationship(Category)
    creator = Column(String(80), ForeignKey('user.email'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'date': str(self.date),
            'category_name': self.category_name,
            'creator': self.creator,
        }


def validate_notspace(input_str):
    if input_str.isspace() or not input_str:
        raise ValidationError('Input cannot be empty')


def verify_user(input_dict):
    schema = UserSchema()
    user = schema.load(input_dict)
    return user


def verify_item(input_dict):
    schema = ItemSchema()
    item = schema.load(input_dict)
    return item


def serialize_item(item):
    schema = ItemSchema()
    return schema.dump(item)


class UserSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    picture = fields.String(required=True)

    @post_load
    def create_user(self, data):
        return User(**data)


class CategorySchema(Schema):
    name = fields.String(required=True)


class ItemSchema(Schema):
    name = fields.String(required=True, validate=validate_notspace)
    description = fields.String(required=True, validate=validate_notspace)
    category_name = fields.String(required=True)
    creator = fields.String(required=True)

    @post_load
    def create_item(self, data):
        return Item(**data)


engine = create_engine(engine_str)

Base.metadata.create_all(engine)
