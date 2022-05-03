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
    
    results2 = Category.query.all()
    #results = Faculty.query.join(Qualified,Faculty.facultyID == Qualified.facultyID) \
   #          .add_columns(Faculty.facultyID, Faculty.facultyName, Qualified.Datequalified, Qualified.courseID)
    return render_template('join.html', title='Join', joined_m_n=results2)
@app.route("/allProducts")
def allProducts():
    
    results2 = Product.query.all()
    #results = Faculty.query.join(Qualified,Faculty.facultyID == Qualified.facultyID) \
   #          .add_columns(Faculty.facultyID, Faculty.facultyName, Qualified.Datequalified, Qualified.courseID)
    return render_template('allProducts.html', title='Products', joined_m_n=results2)

@app.route("/category/<cID>")
def category(cID):
    category = Product.query.filter(Product.Category_id == cID)
    return render_template('about.html', title="Category", category=category, now=datetime.utcnow())

@app.route("/product/<pID>")
def product(pID):
    category = Product.query.filter(Product.ProductID == pID)
    return render_template('viewProduct.html', title="Category", category=category, now=datetime.utcnow())

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
@app.route("/create", methods=['GET', 'POST'])
def create():
    form = CreateForm()
    employeeList = Employee.query.add_columns(Employee.fname, Employee.lname, Employee.ssn)
    projectList = Project.query.add_columns(Project.pnumber)

    if form.validate_on_submit():
        employeeSSN = form.employees.data.split()
        projectNumber = form.projects.data.split()
        assignment = Works_On(essn=int(employeeSSN[2]), pno=int(projectNumber[1]), hours=form.hours.data)
        db.session.add(assignment)
        db.session.commit()
        flash('You successfully added an assignment','success')
        return redirect(url_for('home'))
    
    return render_template('create.html', title="create", form=form)

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
    
    myOrders = Order.query.add_columns(Order.OrderID, Product.ProductName, Product.Price, Order_Detail.Quantity)\
        .filter(Order.CustomerID == current_user.id).\
        join(Order_Detail, Order.OrderID == Order_Detail.OrderID).\
            join(Product, Product.ProductID == Order_Detail.ProductID)
    
    user = str(current_user.id)
    cur = mysql.connection.cursor()
    cur.execute("""SELECT COUNT(orders.OrderID) FROM orders WHERE orders.CustomerID = %s""", [current_user.id])
    ordertotal = cur.fetchall()
    ordertotal = str(*ordertotal[0])
                
    return render_template('myOrders.html', title='myOrders', orders = myOrders, totalOrders= ordertotal)


@app.route("/dept/new", methods=['GET', 'POST'])
@login_required
def new_dept():
    form = DeptForm()
    if form.validate_on_submit():
        dept = Department(dname=form.dname.data, dnumber=form.dnumber.data,mgr_ssn=form.mgr_ssn.data,mgr_start=form.mgr_start.data)
        db.session.add(dept)
        db.session.commit()
        flash('You have added a new department!', 'success')
        return redirect(url_for('home'))
    return render_template('create_dept.html', title='New Department',
                           form=form, legend='New Department')


@app.route("/dept/<dnumber>")
@login_required
def dept(dnumber):
    dept = Department.query.get_or_404(dnumber)
    return render_template('dept.html', title=dept.dname, dept=dept, now=datetime.utcnow())


@app.route("/assign/<pno>/<essn>")
def assign(pno,essn):
    assign = Works_On.query.get_or_404([essn,pno])
    return render_template('assign.html', title=str(assign.essn) + "_" + str(assign.pno), assign=assign, now=datetime.utcnow())




@app.route("/assign/<essn>/<pno>/delete", methods=['POST'])
def delete_assign(essn,pno):
    assign = Works_On.query.get_or_404([essn,pno])
    db.session.delete(assign)
    db.session.commit()
    flash('The assignment has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/dept/<dnumber>/update", methods=['GET', 'POST'])
@login_required
def update_dept(dnumber):
    dept = Department.query.get_or_404(dnumber)
    currentDept = dept.dname

    form = DeptUpdateForm()
    if form.validate_on_submit():          # notice we are are not passing the dnumber from the form
        if currentDept !=form.dname.data:
            dept.dname=form.dname.data
        dept.mgr_ssn=form.mgr_ssn.data
        dept.mgr_start=form.mgr_start.data
        db.session.commit()
        flash('Your department has been updated!', 'success')
        return redirect(url_for('dept', dnumber=dnumber))
    elif request.method == 'GET':              # notice we are not passing the dnumber to the form

        form.dnumber.data = dept.dnumber
        form.dname.data = dept.dname
        form.mgr_ssn.data = dept.mgr_ssn
        form.mgr_start.data = dept.mgr_start
    return render_template('create_dept.html', title='Update Department',
                           form=form, legend='Update Department')




@app.route("/dept/<dnumber>/delete", methods=['POST'])
@login_required
def delete_dept(dnumber):
    dept = Department.query.get_or_404(dnumber)
    db.session.delete(dept)
    db.session.commit()
    flash('The department has been deleted!', 'success')
    return redirect(url_for('home'))
