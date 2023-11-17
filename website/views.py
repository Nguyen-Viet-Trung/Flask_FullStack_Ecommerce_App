from flask import Blueprint, render_template, request, session, flash, redirect, url_for
import sqlite3
views = Blueprint("views", __name__)


sqldbname = 'LAPTRINHWEB.db'

@views.context_processor
def my_utility_processor():
    def convert_currency_to_int(currency_str):
        currency_str = currency_str.replace(".", "").replace(" VNĐ", "")
        return int(currency_str)
    def convert_int_to_currency(number):
        number_str = str(number)
        currency_str = ""
        count = 0

        for digit in reversed(number_str):
            if count != 0 and count % 3 == 0:
                currency_str = "." + currency_str
            currency_str = digit + currency_str
            count += 1

        currency_str += " VNĐ"
        return currency_str
    return dict(convert_currency_to_int=convert_currency_to_int, convert_int_to_currency=convert_int_to_currency)

@views.route('/')
def home():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM FASHION LIMIT 0, 4'
    cursor.execute(sqlcommand)
    featuresProduct = cursor.fetchall()
    sqlcommand = 'SELECT * FROM FASHION LIMIT 2, 10'
    cursor.execute(sqlcommand)
    latestProducts = cursor.fetchall()
    return render_template('home.html', featuresProduct=featuresProduct, latestProducts=latestProducts)

@views.route('/cart', methods=['GET'])
def shopping_cart():
    # current_username = ""
    current_cart = []
    # if 'current_user' in session:
    #     current_username = session['current_user']['name']
    # else:
    #     current_username = ""
    if 'cart' in session:
        current_cart = session.get('cart', [])

    return render_template('cart.html', cart=current_cart)


@views.route('/all_products')
def all_products():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM FASHION'
    cursor.execute(sqlcommand)
    all_products = cursor.fetchall()
    return render_template('all_products.html', all_products=all_products)

@views.route('/product_detail/<id>')
def product_detail(id):
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM FASHION WHERE id = ?'
    cursor.execute(sqlcommand, (id,))
    product_detail = cursor.fetchone()
    sqlcommand = 'SELECT * FROM FASHION LIMIT 0, 4'
    cursor.execute(sqlcommand)
    related_products = cursor.fetchall()
    return render_template('product_detail.html', product_detail=product_detail, related_products=related_products)

@views.route('/about')
def about():
    return render_template('about.html')


@views.route('/contact')
def contact():
    return render_template('contact.html')

@views.route('/cart/add', methods=['POST'])
def addToCart():
    productId = request.form['product_id']
    quantity = int(request.form['quantity'])
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product, price, picture FROM FASHION WHERE id = ?", (productId,))
    product = cursor.fetchone()
    conn.close()
    product_detail = {
        "id": productId,
        "name": product[0],
        "price": product[1],
        "image": product[2],
        "quantity": quantity
    }
    cart = session.get('cart', [])
    found = False
    for item in cart:
        if item["id"] == productId:
            item["quantity"] += quantity
            found = True
            break
    if not found:
        cart.append(product_detail)
    session["cart"] = cart
    rows = len(cart)
    flash('Item added successfully!', 'success')
    # messages = ("Product added successfully! <br> Current:" +
    #             str(rows) + " products" + "<br/><a class='btn btn-primary' href='/cart'>view cart</a><br/> <a class='btn btn-primary' href='/'>home</a>")
    return redirect(url_for('views.product_detail', id=productId))
