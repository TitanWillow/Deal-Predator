from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import bcrypt
from flask import make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from srapper import get_product;
from telegramsend import *;

app = Flask(__name__)
app.secret_key = 'hashedey'
login_manager = LoginManager(app)
login_manager.login_view = 'auth'

class User(UserMixin):
    def __init__(self, id, email, telegram_name):
        self.id = id
        self.email = email
        self.telegram_name = telegram_name

users = {}
# Initialize the database
def init_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            userid INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT UNIQUE,
                            name TEXT,
                            telegram_name text,
                            chat_id text,
                            registered boolean,
                            password TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_map (
                            product_id TEXT NOT NULL,
                            userid TEXT NOT NULL,
                            target1 REAL,
                            target2 REAL,
                            targetpct1 REAL,
                            targetpct2 REAL,
                            FOREIGN KEY (product_id) REFERENCES products(id),
                            FOREIGN KEY (userid) REFERENCES users(userid)
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS initial_entry (
                            product_url TEXT NOT NULL,
                            price REAL,
                            email TEXT,
                            telegram_name text,
                            target1 REAL,
                            target2 REAL,
                            targetpct1 REAL,
                            targetpct2 REAL
                        )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_url TEXT NOT NULL,
            product_name TEXT NOT NULL,
            class TEXT,
            price REAL,
            shopping_site TEXT
        )
        ''')
        
@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, telegram_name FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return User(id=result[0], email=result[1], telegram_name = result[2])
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
    #email = request.form['email']
    telegram_name = request.form['telegram_name']
    password = request.form['password']

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE telegram_name = ?", (telegram_name,))
        result = cursor.fetchone()

        # Check if the user exists and the password is correct
        if result and bcrypt.checkpw(password.encode('utf-8'), result[1]):
            user = User(id=result[0], telegram_name=telegram_name)
            login_user(user)  # Log the user in
            flash('Sign In successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return redirect(url_for('auth', type='signin'))



@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    #email = request.form['email']
    telegram_name = request.form['telegram_name']
    password = request.form['password']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        try:
            if telegram_name is not None:
                cursor.execute("SELECT telegram_name, registered FROM users WHERE telegram_name = ?", (telegram_name,))
                result = cursor.fetchone()
                if result and result[1] is True:
                    flash('Telegram Id already registered. Please sign in.', 'warning')
                else:
                    if get_chat_id(telegram_name) == False:
                        flash('Please send a message to the bot or check the entered username')
                    else :
                        if result[1] is False:
                            cursor.execute("UPDATE users SET password = ?, registered = ? WHERE telegram_name = ?",(hashed_password, True, telegram_name))
                            conn.commit()
                            flash('Sign Up successful! Please sign in.', 'success')
                        else:
                            cursor.execute("INSERT INTO users (name, telegram_name, password, registered) VALUES (?, ?, ?, ?)", (name, telegram_name, hashed_password, True))
                            conn.commit()
                            flash('Sign Up successful! Please sign in.', 'success') 
        except sqlite3.IntegrityError:
            flash('Telegram Id already registered. Please sign in.', 'warning')

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

@app.route('/add', methods=['POST'])
def add_data():
    product_url = request.form['url']
    price = request.form['price']
    #email = request.form['email']
    telegram_name = request.form['telegram_name']
    target_mode = request.form.get('target_mode', 'standard')  # Default to 'standard'
    target1 = request.form.get('target1', None)
    target2 = request.form.get('target2', None)

    targetpct1 = targetpct2 = None

    if target_mode == "percentage":
        targetpct1 = target1
        targetpct2 = target2
        target1 = target2 = None

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO initial_entry 
                          (product_url, price, telegram_name, target1, target2, targetpct1, targetpct2) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (product_url, price, telegram_name, target1, target2, targetpct1, targetpct2))
        conn.commit()
    url=[product_url]
    get_product(url,True, price)
    print(price)
    flash('Data added successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
