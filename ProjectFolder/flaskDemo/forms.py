from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SelectField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
# from flaskDemo import db
from flaskDemo.models import Category, Customer, Order, Order_Detail, Product,Supplier
# from wtforms.fields.html5 import DateField

# ssns = []#Department.query.with_entities(Department.mgr_ssn).distinct()
# #  or could have used ssns = db.session.query(Department.mgr_ssn).distinct()
# # for that way, we would have imported db from flaskDemo, see above

# myChoices2 = [(row[0],row[0]) for row in ssns]  # change
# results=list()
# for row in ssns:
#     rowDict=row._asdict()
#     results.append(rowDict)
# myChoices = [(row['mgr_ssn'],row['mgr_ssn']) for row in results]
# regex1='^((((19|20)(([02468][048])|([13579][26]))-02-29))|((20[0-9][0-9])|(19[0-9][0-9]))-((((0[1-9])'
# regex2='|(1[0-2]))-((0[1-9])|(1\d)|(2[0-8])))|((((0[13578])|(1[02]))-31)|(((0[1,3-9])|(1[0-2]))-(29|30)))))$'
# regex=regex1 + regex2


"""
16. Checks for empty fields using WTForms validation
"""
class PurchaseForm(FlaskForm):
    productList = Product.query.add_columns(Product.ProductID,Product.ProductName,Product.Category_id, Product.Price,Product.Amount_left)
    pList = []
    
    
    for row in productList:
        pList.append((str(row['ProductID']) + " " + row['ProductName'] + " "+ str(row['Price']) + " " + str(row['Amount_left']),row['ProductName'] + "   $"+ str(row['Price']) + "  Quantity:" + str(row['Amount_left'])))
    address = StringField('Enter Address', validators=[DataRequired()])
    products = SelectField('Products', choices = pList, coerce = str)
    amount = IntegerField('Quantity', validators=[DataRequired()]) #make it so u can purchase more than available
    submit = SubmitField("Buy")
    

class RegistrationForm(FlaskForm):
    name = StringField('Full Name',
                        validators=[DataRequired(), Length(min=2, max=20)])                       
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address',
                        validators=[DataRequired()])
    phone = StringField("Phone Number",
                        validators=[DataRequired(), Length(min=10, max=11)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, name):
        user = Customer.query.filter_by(CustomerName=name.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = Customer.query.filter_by(CustomerEmail=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    email = StringField('Update My Email',
                        validators=[DataRequired(), Email()])
    
    submit = SubmitField('Update')
    def validate_email(self, email):
        if email.data != current_user.CustomerEmail:
            user = Customer.query.filter_by(CustomerEmail=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
