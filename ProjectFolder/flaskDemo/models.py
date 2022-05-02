from datetime import datetime
from flaskDemo import db, login_manager
from flask_login import UserMixin
from functools import partial
from sqlalchemy import orm

db.Model.metadata.reflect(db.engine)

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))


class Customer(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    CustomerName = db.Column(db.String(30), unique=True, nullable=False)
    CustomerEmail = db.Column(db.String(120), unique=True, nullable=False)
    CustomerAddress = db.Column(db.String(70), unique=True, nullable=False)
    CustomerPhoneNumber = db.Column(db.String(11), nullable=False)
    Password = db.Column(db.String(60), nullable=False)
    

    def __repr__(self):
        return f"Customer('{self.CustomerName}', '{self.CustomerEmail}', '{self.id}')"


class Post(db.Model):
     __table_args__ = {'extend_existing': True}
     id = db.Column(db.Integer, primary_key=True)
     title = db.Column(db.String(100), nullable=False)
     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
     content = db.Column(db.Text, nullable=False)
     user_id = db.Column(db.Integer, db.ForeignKey('Customer.id'), nullable=False)

     def __repr__(self):
         return f"Post('{self.title}', '{self.date_posted}')"






class Category(db.Model):
    __table__ = db.Model.metadata.tables['Category']
    


# used for query_factory
def getDepartment(columns=None):
    u = Department.query
    if columns:
        u = u.options(orm.load_only(*columns))
    return u

def getDepartmentFactory(columns=None):
    return partial(getDepartment, columns=columns)

class Order(db.Model):
    __table__ = db.Model.metadata.tables['Orders']
    
class Order_Detail(db.Model):
    __table__ = db.Model.metadata.tables['order_detail']
class Product(db.Model):
    __table__ = db.Model.metadata.tables['Product']
class Supplier(db.Model):
    __table__ = db.Model.metadata.tables['Supplier']

    

  
