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
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
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
        conn.commit()
        conn.close()
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')


# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
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
'''@app.route('/admin')
@login_required
def admin_panel():
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates ORDER BY capture_date DESC, capture_time DESC")
    data = c.fetchall()
    conn.close()
    return render_template('admin_panel.html', data=data)'''
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    
    # Initialize query and parameters
    query = "SELECT * FROM plates"
    params = []
    
    # Check if the request method is POST (form submitted)
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        if start_date and end_date:
            query += " WHERE capture_date BETWEEN ? AND ?"
            params.append(start_date)
            params.append(end_date)
        elif start_date:
            query += " WHERE capture_date >= ?"
            params.append(start_date)
        elif end_date:
            query += " WHERE capture_date <= ?"
            params.append(end_date)
    
    query += " ORDER BY capture_date DESC, capture_time DESC"
    c.execute(query, params)
    data = c.fetchall()
    
    # Calculate total paid and unpaid costs
    total_paid = 0
    total_unpaid = 0
    for row in data:
        cost = row[5]  # Assuming the cost is in the 6th column (index 5)
        payment_status = row[6]  # Assuming the payment status is in the 7th column (index 6)
        if payment_status.lower() == 'paid':
            total_paid += cost
        else:
            total_unpaid += cost
    
    conn.close()
    return render_template('admin_panel.html', data=data, total_paid=total_paid, total_unpaid=total_unpaid)

'''@app.route('/track_plate', methods=['GET', 'POST'])
@login_required
def track_plate():
    if request.method == 'POST':
        plate_text = request.form['plate_text']
        # Retrieve plate information from the database based on the plate text
        conn = sqlite3.connect('plates.db')
        c = conn.cursor()
        c.execute("SELECT * FROM plates WHERE plate_text=?", (plate_text,))
        plate_data = c.fetchall()
        conn.close()
        return render_template('track_plate.html', plate_data=plate_data)
    return render_template('track_plate.html')'''
@app.route('/track_plate', methods=['GET', 'POST'])
@login_required
def track_plate():
    plate_data = []
    total_paid = 0
    total_unpaid = 0
    
    if request.method == 'POST':
        plate_text = request.form['plate_text']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        query = "SELECT * FROM plates WHERE plate_text=?"
        params = [plate_text]
        
        if start_date and end_date:
            query += " AND capture_date BETWEEN ? AND ?"
            params.append(start_date)
            params.append(end_date)
        elif start_date:
            query += " AND capture_date >= ?"
            params.append(start_date)
        elif end_date:
            query += " AND capture_date <= ?"
            params.append(end_date)
        
        conn = sqlite3.connect('plates.db')
        c = conn.cursor()
        c.execute(query, params)
        plate_data = c.fetchall()
        
        for row in plate_data:
            cost = row[5]  # Assuming the cost is in the 6th column (index 5)
            payment_status = row[6]  
            if payment_status.lower() == 'paid':
                total_paid += cost
            else:
                total_unpaid += cost
        
        conn.close()
        
    return render_template('track_plate.html', plate_data=plate_data, total_paid=total_paid, total_unpaid=total_unpaid)

@app.route('/view_plate', methods=['POST'])
def view_plate():
    plate_id = request.form['plate_id']
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates WHERE id=?", (plate_id,))
    plate_data = c.fetchone()
    conn.close()
    return render_template('view_plate.html', plate_data=plate_data)

@app.route('/confirm_delete', methods=['POST'])
def confirm_delete():
    plate_id = request.form['plate_id']
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("DELETE FROM plates WHERE id=?", (plate_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/modify_plate', methods=['POST'])
def modify_plate():
    plate_id = request.form['plate_id']
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates WHERE id=?", (plate_id,))
    plate_data = c.fetchone()
    conn.close()
    return render_template('modify_plate.html', plate_data=plate_data)

# Route to confirm modification of a captured plate
@app.route('/confirm_modify', methods=['POST'])
def confirm_modify():
    plate_id = request.form['plate_id']
    new_plate_text = request.form['plate_text']  # Example, assuming there's a text input for plate text
    # Implement logic to modify plate details in the database based on the plate ID
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("UPDATE plates SET plate_text=? WHERE id=?", (new_plate_text, plate_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
