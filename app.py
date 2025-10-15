from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form['name']
        cookie = request.form['cookie']
        quantity = request.form['quantity']
        pickup_time = request.form['pickup_time']

        return render_template('confirmation.html', name=name, cookie=cookie, quantity=quantity, pickup_time=pickup_time)

    return render_template('order.html')

if __name__ == '__main__':
    app.run(debug=True)