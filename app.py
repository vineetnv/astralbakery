import csv, os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey123" 
COOKIES_FILE = 'cookies.csv'
IMAGE_FOLDER = 'static/images'

# ------------------------
# Helper Functions
# ------------------------
def read_cookies():
    cookies = []
    try:
        with open(COOKIES_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['price'] = float(row['price'])
                row['is_listed'] = row['is_listed'] == 'True'
                cookies.append(row)
    except FileNotFoundError:
        pass
    return cookies

def write_cookies(cookies):
    with open(COOKIES_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'name', 'image', 'price', 'is_listed']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for cookie in cookies:
            writer.writerow(cookie)

# ------------------------
# Homepage
# ------------------------
@app.route('/')
def home():
    cookies = read_cookies()
    current_cookies = [c for c in cookies if c['is_listed']]
    past_cookies = [c for c in cookies if not c['is_listed']]
    cart = session.get('cart', {})  # get cart from session
    return render_template('index.html', current_cookies=current_cookies, past_cookies=past_cookies, cart=cart)

# ------------------------
# Add to Cart
# ------------------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    cookie_id = request.form.get('cookie_id')
    quantity = int(request.form.get('quantity', 1))

    cookies = read_cookies()
    cookie = next((c for c in cookies if str(c['id']) == str(cookie_id)), None)
    if not cookie:
        flash("Cookie not found.")
        return redirect(url_for('home'))

    cart = session.get('cart', {})
    if cookie_id in cart:
        cart[cookie_id]['quantity'] += quantity
    else:
        cart[cookie_id] = {
            'name': cookie['name'],
            'price': cookie['price'],
            'quantity': quantity
        }
    session['cart'] = cart
    flash(f"Added {quantity} x {cookie['name']} to cart.")
    return redirect(url_for('home'))

# ------------------------
# Menu Page
# ------------------------
@app.route('/menu')
def menu_page():
    return render_template('menu.html')

# ------------------------
# About Page
# ------------------------
@app.route('/about')
def about_page():
    return render_template('about.html')

# ------------------------
# Order Form
# ------------------------
@app.route('/order', methods=['GET', 'POST'])
def order_page():
    if request.method == 'POST':
        name = request.form['name']
        cookie = request.form['cookie']
        quantity = request.form['quantity']
        pickup_time = request.form['pickup_time']

        with open('orders.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, cookie, quantity, pickup_time])

        return render_template('confirmation.html', name=name, cookie=cookie, quantity=quantity, pickup_time=pickup_time)

    return render_template('order.html')

# ------------------------
# Bakery Owner Login
# ------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'bakeryowner' and password == 'cookie123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return "Incorrect username or password. Try again."

    return render_template('login.html')

# ------------------------
# Dashboard
# ------------------------
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

# ------------------------
# Logout
# ------------------------
@app.route('/logout')
def logout_page():
    session.pop('logged_in', None)
    flash("Successfully logged out")
    return redirect(url_for('home'))

# ------------------------
# Private Orders Page
# ------------------------
@app.route('/orders')
def orders_page():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    orders = []
    try:
        with open('orders.csv', newline='') as file:
            reader = csv.reader(file)
            orders = list(reader)
    except FileNotFoundError:
        orders = []

    return render_template('orders.html', orders=orders)

# ------------------------
# Fulfill Order
# ------------------------
@app.route('/fulfill/<int:order_index>', methods=['POST'])
def fulfill_order(order_index):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    orders = []
    try:
        with open('orders.csv', newline='') as file:
            reader = csv.reader(file)
            orders = list(reader)
    except FileNotFoundError:
        orders = []

    if 0 <= order_index < len(orders):
        orders.pop(order_index)
        with open('orders.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(orders)

    return redirect(url_for('orders_page'))

# ------------------------
# Cookie Management Pages
# ------------------------
@app.route('/manage-cookies')
def manage_cookies():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    
    cookies = read_cookies()
    listed = [c for c in cookies if c['is_listed']]
    not_listed = [c for c in cookies if not c['is_listed']]

    return render_template('manage_cookies.html', listed=listed, not_listed=not_listed)

@app.route('/swap_cookie/<int:id>')
def swap_cookie(id):
    cookies = read_cookies()
    for cookie in cookies:
        if int(cookie['id']) == id:
            cookie['is_listed'] = not cookie['is_listed']
            break
    write_cookies(cookies)
    return redirect(url_for('manage_cookies'))

@app.route('/remove_cookie/<int:id>')
def remove_cookie(id):
    cookies = [c for c in read_cookies() if int(c['id']) != id]
    write_cookies(cookies)
    return redirect(url_for('manage_cookies'))

@app.route('/add_cookie', methods=['GET', 'POST'])
def add_cookie():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.files['image']

        if image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(IMAGE_FOLDER, filename))
            image_path = f'images/{filename}'
        else:
            image_path = 'images/default.jpg'

        cookies = read_cookies()
        new_id = max([int(c['id']) for c in cookies], default=0) + 1
        cookies.append({
            'id': new_id,
            'name': name,
            'image': image_path,
            'price': price,
            'is_listed': True
        })
        write_cookies(cookies)
        return redirect(url_for('manage_cookies'))
    return render_template('add_cookie.html')

@app.route('/update_cookie/<int:id>', methods=['POST'])
def update_cookie(id):
    cookies = read_cookies()
    for cookie in cookies:
        if int(cookie['id']) == id:
            cookie['name'] = request.form['name']
            cookie['price'] = request.form['price']
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                image.save(os.path.join(IMAGE_FOLDER, filename))
                cookie['image'] = f'images/{filename}'
            break
    write_cookies(cookies)
    return redirect(url_for('manage_cookies'))

# ------------------------
# Run Flask App
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)