import csv
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Change to a random string for security

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

        # Set your friend's credentials
        if username == 'bakeryowner' and password == 'cookie123':
            session['logged_in'] = True
            return redirect(url_for('orders_page'))
        else:
            return "Incorrect username or password. Try again."

    return render_template('login.html')

# ------------------------
# Logout
# ------------------------
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
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
# Run Flask App
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)