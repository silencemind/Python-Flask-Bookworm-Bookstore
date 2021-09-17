#!/usr/local/bin/python3

from flask import *
import shelve
import sqlite3, hashlib, os,uuid
from werkzeug.utils import secure_filename
from persistance import *


app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def root():

    list_array,list_rec = get_all_books()
    return render_template('home.html', itemData=list_array,itemRec=list_rec)

@app.route("/add")
def add():
    return render_template('add.html', categories=['Fiction', 'Thriller', 'Novel', 'Poetry'])


@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        category = request.form['category']



        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        

        msg="error occured"
        try:
            create_book(name, price, description, imagename, stock, category)
            msg="added successfully"
        finally:
            pass

        print(msg)
        return redirect(url_for('add'))

@app.route("/edit")
def edit():
    
    busdata=shelve.open("test_shelf.db")
    my_keys = list(busdata.keys())
    my_keys.sort()
    list_array = []
    for lctno in my_keys:
        a = list(busdata[ lctno ].values())
        list_array.append(a)
    busdata.close()
    print(list_array)
    return render_template('edit.html', data=list_array)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    s = shelve.open('test_shelf.db')
    msg="error occured"
    try:
        del s[productId]
        msg="Deleted successfully"
    finally:
        s.close()
        print(msg)
        return redirect(url_for('root'))


@app.route("/updateItem", methods=["GET", "POST"])
def updateItem():
    print(request.method)
    if request.method == 'GET':
        productId = request.args.get('productId')
        s = shelve.open('test_shelf.db', flag='r')
        try:
            existing = s[productId]
        finally:
            s.close()

        print(list(existing.values()))
        productData = list(existing.values())
        productData[3]
        return render_template("update.html", data=productData, categories=['Fiction', 'Thriller', 'Novel', 'Poetry'])
    else:
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        category = request.form['category']
        image = request.files['image']
        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        s = shelve.open('test_shelf.db',writeback=True)

        
        try:
            if filename:
                imagename = filename
                s[name] = { 'name': name, 'price':price, 'description':description, 'image': imagename, 'stock': stock, 'category': category}
            else:
                s[name]['price'] = price
                s[name]['description'] = description
                s[name]['stock'] = stock
                s[name]['category'] = category

            msg="added successfully"
        finally:
            
            s.close()

        print(msg)
        return redirect(url_for('root'))

@app.route("/productDescription")
def productDescription():
    productId = request.args.get('productId')
    
    s = shelve.open('test_shelf.db', flag='r')
    try:
        existing = s[productId]
    finally:
        s.close()

    print(list(existing.values()))
    productData = list(existing.values())
    return render_template("productDescription.html", data=productData)

@app.route("/addToCart")
def addToCart():
    productId = request.args.get('productId')
    s = shelve.open('order_shelf.db')
    msg="error occured"
    # check if that book was ordered before 

    try:
        existing = s[productId]
    except:
        try:
            s[productId] = {'orders': 1 }
            msg="added successfully"
        finally:
            s.close()
            print(msg)
    print(msg)
    s.close()

    return redirect(url_for('root'))

@app.route("/cart")
def cart():
    data=shelve.open("order_shelf.db")
    my_keys = list(data.keys())
    my_keys.sort()
    list_array = []
    for lctno in my_keys:

        a = list(data[ lctno ].values())
        a.insert(0,lctno)
        
        list_array.append(a)
    data.close()
    print(list_array)
    products = []
    totalPrice = 0
    for item in list_array:
        productId = item[0]
        s = shelve.open('test_shelf.db', flag='r')
        try:
            existing = s[productId]
            print('LOL::::',existing)
            print(list(existing.values()))
            productData = list(existing.values())
            totalPrice += productData[1]
            products.append(productData)
        finally:
            s.close()
    return render_template("cart.html", products = products, totalPrice=totalPrice)


@app.route("/removeFromCart")
def removeFromCart():
    productId = request.args.get('productId')
    s = shelve.open('order_shelf.db')
    msg="error occured"

    try:
        del s[productId]
        msg="added successfully"
    finally:
        s.close()
        print(msg)
        return redirect(url_for('cart'))

@app.route("/checkout", methods=['GET','POST'])
def payment():
    
    busdata=shelve.open("order_shelf.db")
    my_keys = list(busdata.keys())
    my_keys.sort()
    list_array = []
    for lctno in my_keys:
        # print( lctno , tuple(busdata[ lctno ].values()))
        a = list(busdata[ lctno ].values())
        a.insert(0,lctno)
        
        list_array.append(a)
    busdata.close()
    print(list_array)
    products = []
    totalPrice = 0
    for item in list_array:
        productId = item[0]
        s = shelve.open('test_shelf.db', flag='r')
        try:
            existing = s[productId]
        finally:
            s.close()
        print(list(existing.values()))
        productData = list(existing.values())
        totalPrice += productData[1]
        products.append(productData)


    g = shelve.open('order_shelf.db')
    msg="error occured"
    # check if that book was ordered before 

    try:
        for prod in list(g.keys()):
            del g[prod]
        msg="deleted successfully"
    finally:
        g.close()
        print(msg)
        
    
    if request.method == "POST":
        class user_data:
            def __init__(self,id,full_name,book_name,email,address,city,state,zip_code,name_on_card,ccno,exp_month,exp_year,cvv):
                self.id = id
                self.full_name = full_name
                self.book_name = book_name
                self.email = email
                self.address = address
                self.city = city
                self.state = state
                self.zip_code = zip_code
                self.name_on_code = name_on_card
                self.cardnumber = cardnumber
                self.ccno = ccno
                self.exp_month = exp_month
                self.exp_year = exp_year
                self.cvv = cvv


        name = request.form['firstname']
        b_name = request.form['bookname']
        email = request.form['email']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip']
        name_on_card = request.form['cardname']
        cardnumber = request.form['cardnumber']
        cvv = request.form['cvv']
        exp_month = request.form['expmonth']
        exp_year = request.form['expyear']
        id = str(uuid.uuid1())

        

        users = user_data(id,name,b_name,email,address,city,state,zip_code,name_on_card,cardnumber,exp_month,exp_year,cvv)
        s = shelve.open('customer_shelf.db')
        msg="error occured"
        try:

            s[users.id]= {'id':users.id,'Full Name':users.full_name, 'Book Name': users.book_name,'Email ':users.email,'Address: ':users.address,'City':users.city,'State':users.state,'Zip Code':users.zip_code}
            msg="added successfully"
            new_open = open("database.txt","a+")
            for k in s:
                idss = k
                dta = str(s[k])
                reslt = idss+":"+dta
                new_open.write(reslt+"\n")

        finally:
            
            s.sync()

        print(msg)


    return render_template("order_details.html", products = products, totalPrice=totalPrice,show_data=users)




@app.route('/deleteUser/<string:id>', methods=['GET',"POST"]) 
def deleteUser(id):
    db= shelve.open('customer_shelf.db','w')
    fopen = open("database.txt",'a+')
    fopen_dicts = dict(fopen)
    if id in db:
        del db[id]
    if id in fopen:
        del fopen[id]
    db.sync()
    return render_template('home.html',message="USER Deleted")
    

@app.route("/retrieveusers",methods=["GET","POST"])
def retrieveUser():
    db = shelve.open("customer_shelf.db")
    keyss = list(db.keys())
    keyss.sort()
    lists_array = []
    for lctnoo in keyss:
        # print( lctno , tuple(busdata[ lctno ].values()))
        ab = list(db[ lctnoo ].values())
        
        
        lists_array.append(ab)
    total_users = len(db)
    db.close()
    print(lists_array)

    return render_template("retrieve.html",data=lists_array,total_users=total_users)


@app.route("/updateuser/<string:id>",methods=["POST"])
def updateuser(id):
    if request.method == "POST":

        db = shelve.open('customer_shelf.db')
        users = db[id]
        user_name = users.get('Full Name')
        book = users.get("Book Name")
        email = users.get("Email ")
        address = users.get("Address: ")
        city = users.get("City")
        state = users.get("State")
        zip_code = users.get("Zip Code")

        db[id] = users
        print (db[id])
        msg = "UPDATED"
        db.close()
        return render_template('update_users.html',id=id,user_name=user_name,book=book,email=email,address=address,city=city,state=state,zip_code=zip_code,msg=msg)

    else:
        pass

@app.route("/updated/<string:id>",methods=["POST"])
def updated(id):
    db = shelve.open('customer_shelf.db','w')
    user = request.form['name']
    book = request.form['book']
    email = request.form['email']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    zip_code = request.form['zip']

    db[id]= {'id':id,'Full Name':user, 'Book Name':book,'Email ':email,'Address: ':address,'City':city,'State':state,'Zip Code':zip_code}

    msg="Updated User"
    return render_template("retrieve.html",msg=msg)

@app.route("/billing", methods=['GET','POST'])
def billing():
    return render_template("billing.html")


if __name__ == '__main__':
    app.run(debug=True)



       #asdasd