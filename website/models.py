from . import db 
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    unit = db.Column(db.String(100))
    notes = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class OpenOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    price = db.Column(db.Float)
    unit = db.Column(db.String(100))
    amount = db.Column(db.Float)
    r_total = db.Column(db.Float)
    order_placed = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.Column(db.String(100))
    vendor = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class ClosedOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    open_order_id = db.Column(db.Integer, db.ForeignKey('open_order.id'))
    item = db.Column(db.String(100))
    price = db.Column(db.Float)
    unit = db.Column(db.String(100))
    amount = db.Column(db.Float)
    r_total = db.Column(db.Float)
    order_placed = db.Column(db.DateTime)
    order_completed = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.Column(db.String(100))
    vendor = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vendor = db.Column(db.String(100))


from hashlib import md5

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), index=True, nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    B_name = db.Column(db.String(150), index=True, nullable=False, unique=True)
    B_type = db.Column(db.String(20), nullable=False)
    about_us = db.Column(db.String(10000))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    items = db.relationship('Item', backref='owner', lazy='dynamic')
    open_orders = db.relationship('OpenOrder', backref='seller', lazy='dynamic')
    closed_orders = db.relationship('ClosedOrder', backref='seller', lazy='dynamic')
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

#in terminal: flask db migrate
#then: flask db upgrade
