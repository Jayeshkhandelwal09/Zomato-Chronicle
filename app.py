from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import json
from models import db , MenuItem, Order, OrderedItem

app = Flask(__name__)
app.secret_key = 'Jayesh'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Jayesh%400709@localhost:3306/zomato'
db.init_app(app)



# Load menu and orders from JSON files
def load_menu():
    try:
        with open('data/menu.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Menu file not found. Creating an empty menu.")
        return []
    except json.JSONDecodeError:
        print("Error decoding the menu file. Creating an empty menu.")
        return []

def load_orders():
    try:
        with open('data/orders.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Orders file not found. Creating an empty orders list.")
        return []
    except json.JSONDecodeError:
        print("Error decoding the orders file. Creating an empty orders list.")
        return []

menu = load_menu()
orders = load_orders()

# Function to save the menu to a JSON file with error handling
def save_menu_to_json(menu):
    try:
        with open('data/menu.json', 'w') as file:
            json.dump(menu, file)
    except IOError:
        print("Error saving menu to file.")

# Function to save orders to a JSON file with error handling
def save_orders_to_json(orders):
    try:
        with open('data/orders.json', 'w') as file:
            json.dump(orders, file)
    except IOError:
        print("Error saving orders to file.")

# Define routes and their corresponding functions here

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menu')
def index():
    menu = MenuItem.query.all()
    return render_template('menu.html', menu=menu)

@app.route('/add_dish', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        dish_id = request.form['dish_id']
        dish_name = request.form['dish_name']
        dish_price = request.form['dish_price']
        dish_available = 'available' in request.form  # Checkbox

        if not dish_id or not dish_name or not dish_price:
            flash('All fields are required.')
        else:
            try:
                dish_price = float(dish_price)
            except ValueError:
                flash('Invalid price format. Please enter a numeric value.')
            else:
                new_dish = MenuItem(
                    name=dish_name,
                    description='',
                    price=dish_price,
                    available=dish_available
                )
                db.session.add(new_dish)
                db.session.commit()
                flash(f"Hooray! {dish_name} has been added to the menu. 🚀")
                return redirect(url_for('index'))

    return render_template('add_dish.html')

@app.route('/remove_dish', methods=['GET', 'POST'])
def remove_dish():
    if request.method == 'POST':
        dish_id_to_remove = request.form.get('dish_id_to_remove')
        dish_to_remove = MenuItem.query.get(dish_id_to_remove)

        if dish_to_remove:
            db.session.delete(dish_to_remove)
            db.session.commit()
            flash(f"Dish with ID {dish_id_to_remove} has been removed from the menu.")
        else:
            flash(f"Dish with ID {dish_id_to_remove} not found in the menu.")

    return render_template('remove_dish.html')

@app.route('/update_availability', methods=['GET', 'POST'])
def update_availability():
    if request.method == 'POST':
        dish_id_to_update = request.form.get('dish_id_to_update')
        dish_to_update = MenuItem.query.get(dish_id_to_update)

        if dish_to_update:
            dish_to_update.available = not dish_to_update.available
            db.session.commit()
            flash(f"Availability of Dish with ID {dish_id_to_update} has been updated.")
        else:
            flash(f"Dish with ID {dish_id_to_update} not found in the menu.")

    return render_template('update_avail.html')

@app.route('/take_order', methods=['GET', 'POST'])
def take_order():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        ordered_dishes = []

        for dish in MenuItem.query.all():
            dish_id = dish.id
            quantity = request.form.get(f'dish_{dish_id}')
            if quantity and quantity.isdigit():
                quantity = int(quantity)
                if quantity > 0:
                    ordered_dishes.append({
                        'id': dish_id,
                        'quantity': quantity,
                    })

        if not customer_name or not ordered_dishes:
            flash('Customer name and at least one dish selection are required.')
        else:
            total_price = sum(
                dish['quantity'] * MenuItem.query.get(dish['id']).price
                for dish in ordered_dishes
            )

            new_order = Order(
                customer_name=customer_name,
                total_price=total_price
            )
            db.session.add(new_order)
            db.session.commit()

            for dish in ordered_dishes:
                ordered_item = OrderedItem(
                    order_id=new_order.id,
                    menu_item_id=dish['id'],
                    quantity=dish['quantity']
                )
                db.session.add(ordered_item)
                db.session.commit()

            flash(f"Order placed with ID: {new_order.id}, Total Price: ${total_price:.2f}")
            return redirect(url_for('home'))

    return render_template('take_order.html', menu=MenuItem.query.all())

@app.route('/update_order_status', methods=['GET', 'POST'])
def update_order_status():
    if request.method == 'POST':
        order_id_to_update = request.form.get('order_id_to_update')
        new_status = request.form.get('new_status')

        order_to_update = Order.query.get(order_id_to_update)

        if order_to_update:
            order_to_update.status = new_status
            db.session.commit()
            flash(f"Status for Order ID {order_id_to_update} updated to {new_status}.")
        else:
            flash(f"Order with ID {order_id_to_update} not found.")

    return render_template('update_status.html')

@app.route('/review_all_orders')
def review_all_orders():
    orders = Order.query.all()
    return render_template('review_orders.html', orders=orders)

@app.route('/filter_orders_by_status', methods=['GET', 'POST'])
def filter_orders_by_status():
    if request.method == 'POST':
        status_to_filter = request.form.get('status_to_filter')

        filtered_orders = Order.query.filter_by(status=status_to_filter).all()

        return render_template('filtered_orders.html', filtered_orders=filtered_orders)

    return render_template('filter_status.html')

if __name__ == '__main__':
    app.run(debug=True)
