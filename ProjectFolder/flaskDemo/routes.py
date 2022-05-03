import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import PurchaseForm, LoginForm, UpdateAccountForm, RegistrationForm
from flaskDemo.models import Post,Category, Customer, Order, Order_Detail, Product, Supplier
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from flask_mysqldb import MySQL

"""
Edit these values to your specific info, including port
"""
app.config["MYSQL_USER"] = "tab"
app.config["MYSQL_PASSWORD"] = "bart"
app.config["MYSQL_DB"] = "ecommerce"
app.config["MYSQL_PORT"] = 3306
mysql = MySQL(app)


@app.route("/")
@app.route("/home")
def home():
    """
    8. Simple SQL query
    """
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM CATEGORY""")
    results2 = cur.fetchall()
    return render_template('join.html', title='Join', joined_m_n=results2)

@app.route("/allProducts")
def allProducts():
    
    results2 = Product.query.all()
    #results = Faculty.query.join(Qualified,Faculty.facultyID == Qualified.facultyID) \
   #          .add_columns(Faculty.facultyID, Faculty.facultyName, Qualified.Datequalified, Qualified.courseID)
    return render_template('allProducts.html', title='Products', joined_m_n=results2)

@app.route("/category/<cID>")
def category(cID):
    cur = mysql.connection.cursor()
    """ 11. COMPOUND CONDITION """
    """sqlAlchemy equivalent: category = Product.query.filter(Product.Category_id == cID, product.Amount_left > 0 )"""
    cur.execute("""SELECT * FROM product WHERE product.Category_id = %s AND product.Amount_left > 0""", [cID])
    category = cur.fetchall()
    return render_template('about.html', title="Category", category=category, now=datetime.utcnow())

@app.route("/suppliers")
def suppliers():
    suppliers = Category.query.add_columns(Category.Categoryname,Supplier.Name,Supplier.phoneNumber).\
        join(Product, Category.Category_id == Product.Category_id).\
            join(Supplier, Supplier.SupplierID == Product.SupplierID)

    return render_template('ourSuppliers.html', title="Suppliers", suppliers=suppliers, now=datetime.utcnow())


@app.route("/product/<pID>")
def product(pID):
    category = Product.query.filter(Product.ProductID == pID)
    return render_template('viewProduct.html', title="Category", category=category, now=datetime.utcnow())


"""
6. UPDATE of a record
"""
@app.route("/edit", methods=['GET', 'POST'])
@login_required
def edit():
    user = Customer.query.get_or_404(current_user.id)
    userEmail = user.CustomerEmail

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if userEmail != form.email.data:
            user.CustomerEmail = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    
    
    return render_template('editAccount.html', title='edit', form=form)

"""
5. Create/insert a record
14. Form to collect user data
15. Product field is populated from the database
"""
@app.route("/purchase", methods=['GET', 'POST'])
@login_required
def purchase():
    form = PurchaseForm()
    if form.validate_on_submit():
        currentDate = str(datetime.utcnow()).split()
        product = form.products.data.split()
        #make order
        order = Order(Date = currentDate[0], ShippingAddress = form.address.data, CustomerID = current_user.id)
        db.session.add(order)
        db.session.commit()
        #make composite order
        order_dets = Order_Detail(OrderID = order.OrderID, ProductID = product[0],Quantity=form.amount.data)
        db.session.add(order_dets)
        db.session.commit()

        

        flash('Thank you for your purchase!','success')
        return redirect(url_for('home'))
    
    return render_template('purchase.html', title="create", form=form)

"""
7. Delete a record
"""
@app.route("/delete/<int:OrderID>", methods=['POST'])
@login_required
def delete_order(OrderID):
    order = Order.query.get_or_404(OrderID)
    db.session.delete(order)
    db.session.commit()
    flash('The order has been deleted!', 'success')
    return redirect(url_for('account'))



@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Customer(CustomerName=form.name.data, CustomerAddress = form.address.data, CustomerPhoneNumber = form.phone.data,Password=hashed_password,CustomerEmail=form.email.data )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        """
        9. Filter by query
        """
        user = Customer.query.filter_by(CustomerEmail=form.email.data).first()
        if user and bcrypt.check_password_hash(user.Password, form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    #Want to query all the orders of customerID and get the name of the product
    cur = mysql.connection.cursor()

    """myOrders = Order.query.add_columns(Order.OrderID, Product.ProductName, Product.Price, Order_Detail.Quantity)\
        .filter(Order.CustomerID == current_user.id).\
        join(Order_Detail, Order.OrderID == Order_Detail.OrderID).\
            join(Product, Product.ProductID == Order_Detail.ProductID)"""
    
    """
    12. JOIN QUERY USING SQL and 13. SUBQUERY USING SQL
    """
    cur.execute("""SELECT Orders.OrderID, Product.ProductName, Product.Price, order_detail.Quantity FROM ((Orders INNER JOIN order_detail ON Orders.OrderID = order_detail.OrderID) INNER JOIN Product ON order_detail.ProductID = Product.ProductID) WHERE Orders.CustomerID IN (SELECT id FROM Customer WHERE id = %s )""", [current_user.id])
    myOrders = cur.fetchall()
    
    """ 10. AGGREGATE FUNCTION """
    cur.execute("""SELECT COUNT(orders.OrderID) FROM orders WHERE orders.CustomerID = %s""", [current_user.id])
    ordertotal = cur.fetchall()
    ordertotal = str(*ordertotal[0])
                
    return render_template('myOrders.html', title='myOrders', orders = myOrders, totalOrders= ordertotal)
