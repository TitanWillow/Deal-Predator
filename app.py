from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import bcrypt
from flask import make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'hashedey'
login_manager = LoginManager(app)
login_manager.login_view = 'auth'

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

users = {}
# Initialize the database
def init_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT UNIQUE,
                            name TEXT,
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
        
@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return User(id=result[0], email=result[1])
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # or another page
    form_type = request.args.get('type', 'signin')  # Default to 'signin'
    return render_template('auth.html', form_type=form_type)

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()

        # Check if the user exists and the password is correct
        if result and bcrypt.checkpw(password.encode('utf-8'), result[1]):
            user = User(id=result[0], email=email)
            login_user(user)  # Log the user in
            flash('Sign In successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return redirect(url_for('auth', type='signin'))



@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
            conn.commit()
            flash('Sign Up successful! Please sign in.', 'success')
        except sqlite3.IntegrityError:
            flash('Email already registered. Please sign in.', 'warning')

    return redirect(url_for('auth', type='signin'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    response = make_response(render_template('dashboard.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
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
