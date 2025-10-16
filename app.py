import csv
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Change this to a secure random string

# ------------------------
# Homepage
# ------------------------
@app.route('/')
def home():
    return render_template('index.html')

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

        # Save order to CSV
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

        # Replace with your friend's credentials
        if username == 'bakeryowner' and password == 'cookie123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return "Incorrect username or password. Try again."

    return render_template('login.html')

# ------------------------
# Dashboard (Bakery Owner Homepage)
# ------------------------
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/manage-cookies')
def manage_cookies():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('manage.html')

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
# Fulfill Order (Remove from CSV)
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

    # Remove the order at the given index
    if 0 <= order_index < len(orders):
        orders.pop(order_index)
        with open('orders.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(orders)

    return redirect(url_for('orders_page'))

# ------------------------
# Run Flask App
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)