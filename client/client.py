from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = '87b8e4b5-816f-40ba-871e-0e3d901cf6274873fa9b750c10256c09e2b954a2b595'

login_manager = LoginManager()
login_manager.init_app(app)

# Function to create a connection to the SQLite database
def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Function to create a table for users if it doesn't exist
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    # Drop the user_plates and users tables if they exist
    cursor.execute('''DROP TABLE IF EXISTS user_plates''')
    cursor.execute('''DROP TABLE IF EXISTS users''')
    
    # Create the user_plates table with the correct schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_plates
                      (id INTEGER PRIMARY KEY, user_id INTEGER, plate_text TEXT,
                       FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Create the users table with the correct schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')
    
    conn.commit()
    conn.close()

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

# Loader function for Flask-Login
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

# Route for signing up
# Route for signing up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        plate_text = request.form['plate_text']  # Add plate text field
        
        hashed_password = hash_password(password)
        
        # Check if the username already exists
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return "Username already exists. Please choose a different username."
        
        # If the username is unique, insert the new user into the database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        user_id = cursor.lastrowid  # Get the ID of the newly inserted user
        
        # Insert the plate text associated with the user into the user_plates table
        cursor.execute("INSERT INTO user_plates (user_id, plate_text) VALUES (?, ?)", (user_id, plate_text))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('login_submit'))
    
    return render_template('client_signup.html')


# Route for logging in
@app.route('/login_submit', methods=['GET', 'POST'])
def login_submit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and user[3] == hashed_password:
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj, remember=True)  # Remember the user's session
            return redirect(url_for('admin_panel'))
        else:
            return "Invalid username or password"
    
    return render_template('login.html')
# Route for user profile
@app.route('/profile')
@login_required
def profile():
    return f"Welcome, {current_user.username}!"

# Route for logging out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route for admin panel, protected by login_required
# Route for the admin panel, protected by login_required
@app.route('/admin')
@login_required
def admin_panel():
    # Connect to the users database
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch the plate_text associated with the current user
    cursor.execute("SELECT plate_text FROM user_plates WHERE user_id = ?", (current_user.id,))
    plate_texts = cursor.fetchall()

    # Connect to the plates database
    conn_plates = sqlite3.connect('plates.db')
    c = conn_plates.cursor()

    # Fetch information from the plates table based on the plate_text associated with the current user
    data = []
    for plate_text in plate_texts:
        c.execute("SELECT * FROM plates WHERE plate_text = ?", plate_text)
        data.extend(c.fetchall())

    conn.close()
    conn_plates.close()

    return render_template('admin_panel.html', data=data)



@app.route('/view_plate', methods=['POST'])
def view_plate():
    plate_id = request.form['plate_id']
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates WHERE id=?", (plate_id,))
    plate_data = c.fetchone()
    conn.close()
    return render_template('view_plate.html', plate_data=plate_data)


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
