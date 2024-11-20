from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
users = {}
# Initialize the database
def init_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            password TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            description TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            price REAL,
                            discount REAL,
                            link TEXT)''')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    form_type = request.args.get('type', 'signin')  # Default to 'signin'
    return render_template('auth.html', form_type=form_type)

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    # Check if user exists
    if email in users and users[email]['password'] == password:
        flash('Sign In successful!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to the dashboard
    else:
        flash('Invalid credentials, please try again.', 'danger')

    return redirect(url_for('home'))


@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Add user if not exists
    if email in users:
        flash('Email already registered. Please sign in.', 'warning')
    else:
        users[email] = {'name': name, 'password': password}
        flash('Sign Up successful! Please sign in.', 'success')

    return redirect(url_for('auth', type='signin'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    search_query = request.args.get('q', '').strip()
    query = "SELECT name, price, discount, link FROM products"
    params = []

    if search_query:
        query += " WHERE name LIKE ?"
        params.append(f"%{search_query}%")

    query += " ORDER BY discount DESC"

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        products = cursor.fetchall()

    return render_template('dashboard.html', products=products, search_query=search_query)

@app.route('/seed_products')
def seed_products():
    products = [
        ('Product A', 19.99, 10, 'https://example.com/product-a'),
        ('Product B', 29.99, 20, 'https://example.com/product-b'),
        ('Product C', 39.99, 5, 'https://example.com/product-c'),
    ]
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO products (name, price, discount, link) VALUES (?, ?, ?, ?)", products)
        conn.commit()
    return "Products seeded!"


@app.route('/add', methods=['POST'])
def add_data():
    title = request.form['title']
    description = request.form['description']
    
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO data (title, description) VALUES (?, ?)", (title, description))
        conn.commit()

    # Flash success message
    flash('Data added successfully!', 'success')

    # Redirect to home page
    return redirect(url_for('home'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
