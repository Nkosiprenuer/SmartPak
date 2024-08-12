from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = '87b8e4b5-816f-40ba-871e-0e3d901cf6274873fa9b750c10256c09e2b954a2b595'

login_manager = LoginManager()
login_manager.init_app(app)

def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''DROP TABLE IF EXISTS user_plates''')
    cursor.execute('''DROP TABLE IF EXISTS users''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_plates
                      (id INTEGER PRIMARY KEY, user_id INTEGER, plate_text TEXT,
                       FOREIGN KEY(user_id) REFERENCES users(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    else:
        return None

@app.route('/signup', methods=['GET', 'POST'])
def signup_submit():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        plate_text = request.form['plate_text']

        hashed_password = hash_password(password)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "Username already exists. Please choose a different username."

        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        user_id = cursor.lastrowid

        cursor.execute("INSERT INTO user_plates (user_id, plate_text) VALUES (?, ?)", (user_id, plate_text))

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('client_signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            stored_hashed_password = user[3]
            if stored_hashed_password == hashed_password:
                user_obj = User(user[0], user[1], user[2])
                login_user(user_obj, remember=True)
                return redirect(url_for('admin_panel'))
            else:
                return "Invalid username or password"
        else:
            return "Invalid username or password"
    
    return render_template('client_login.html')

@app.route('/login_submit', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']
    hashed_password = hash_password(password)
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        stored_hashed_password = user[3]
        if stored_hashed_password == hashed_password:
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj, remember=True)
            return redirect(url_for('admin_panel'))
        else:
            return "Invalid username or password"
    else:
        return "Invalid username or password"

@app.route('/profile')
@login_required
def profile():
    return f"{current_user.username},{current_user.email}"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

'''@app.route('/myparking')
@login_required
def admin_panel():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT plate_text FROM user_plates WHERE user_id = ?", (current_user.id,))
    plate_texts = cursor.fetchall()

    conn_plates = sqlite3.connect('plates.db')
    c = conn_plates.cursor()

    data = []
    total_cost = 0
    total_paid = 0

    for plate_text in plate_texts:
        c.execute("SELECT * FROM plates WHERE plate_text = ?", (plate_text[0],))
        plate_records = c.fetchall()

        for record in plate_records:
            data.append(record)
            if record[6] == 'Unpaid':  # Assuming 'Unpaid' is at index 6
                cost = record[5] if record[5] is not None else 0  # Assuming 'cost' is at index 5
                total_cost += cost
                paid = record[7] if record[7] is not None else 0  # Assuming 'amount_paid' is at index 7
                total_paid += paid

    total_balance = total_cost - total_paid

    conn.close()
    conn_plates.close()

    return render_template('myparking.html', data=data, total_cost=total_cost, total_paid=total_paid, total_balance=total_balance)'''
    
@app.route('/myparking')
@login_required
def admin_panel():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT plate_text FROM user_plates WHERE user_id = ?", (current_user.id,))
    plate_texts = cursor.fetchall()

    conn_plates = sqlite3.connect('plates.db')
    c = conn_plates.cursor()

    data = []
    total_cost = 0
    total_paid_cost = 0
    total_unpaid_cost = 0

    for plate_text in plate_texts:
        c.execute("SELECT * FROM plates WHERE plate_text = ?", (plate_text[0],))
        plate_records = c.fetchall()

        for record in plate_records:
            data.append(record)
            cost = record[5] if record[5] is not None else 0  # Assuming 'cost' is at index 5
            total_cost += cost
            if record[6] == 'Unpaid':  # Assuming 'Unpaid' is at index 6
                total_unpaid_cost += cost
            elif record[6] == 'Paid':  # Assuming 'Paid' is at index 6
                total_paid_cost += cost

    conn.close()
    conn_plates.close()

    return render_template('myparking.html', data=data, total_cost=total_cost, total_unpaid_cost=total_unpaid_cost, total_paid_cost=total_paid_cost)

@app.route('/make_payment', methods=['GET', 'POST'])
@login_required
def make_payment():
    if request.method == 'POST':
        plate_text = request.form['plate_text']
        payment_amount = float(request.form['payment_amount'])

        conn = sqlite3.connect('plates.db')
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM plates WHERE plate_text = ?", (plate_text,))
        balance = cursor.fetchone()[0]

        new_balance = balance - payment_amount
        if new_balance <= 0:
            payment_status = 'Paid'
            new_balance = 0
        else:
            payment_status = 'Unpaid'

        cursor.execute("UPDATE plates SET balance = ?, payment_status = ? WHERE plate_text = ?", (new_balance, payment_status, plate_text))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_panel'))

    plate_text = request.args.get('plate_text')
    conn = sqlite3.connect('plates.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plates WHERE plate_text = ?", (plate_text,))
    plate_record = cursor.fetchone()
    conn.close()
    return render_template('make_payment.html', plate_record=plate_record)

if __name__ == '__main__':
    app.run(debug=True)



  


def add_payment_status_and_balance_columns():
    conn = sqlite3.connect('plates.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(plates)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'payment_status' not in columns:
        cursor.execute("ALTER TABLE plates ADD COLUMN payment_status TEXT DEFAULT 'Unpaid'")
    if 'balance' not in columns:
        cursor.execute("ALTER TABLE plates ADD COLUMN balance REAL")

    cursor.execute("UPDATE plates SET balance = cost WHERE balance IS NULL")

    conn.commit()
    conn.close()

add_payment_status_and_balance_columns()

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
