from flask import Flask, render_template, request, redirect, url_for, session
import csv

app = Flask(__name__)
app.secret_key = "supersecretkey123"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/orders')
def view_orders():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    orders = []
    try:
        with open('orders.csv', newline='') as file:
            reader = csv.reader(file)
            orders = list(reader)
    except FileNotFoundError:
        orders = []

    return render_template('orders.html', orders=orders)


# @app.route('/orders-1234')  # change 1234 to a random secret string
# def view_orders():
#     orders = []
#     try:
#         with open('orders.csv', newline='') as file:
#             reader = csv.reader(file)
#             orders = list(reader)
#     except FileNotFoundError:
#         orders = []
#     return render_template('orders.html', orders=orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Replace these with your friend's credentials
        if username == 'bakeryowner' and password == 'cookie123':
            session['logged_in'] = True
            return redirect(url_for('view_orders'))
        else:
            return "Incorrect credentials. Try again."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # removes the login info from the session
    return redirect(url_for('home'))  # send user back to homepage

if __name__ == '__main__':
    app.run(debug=True)