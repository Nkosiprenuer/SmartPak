from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid  # for generating unique tokens

app = Flask(__name__)
app.secret_key = '87b8e4b5-816f-40ba-871e-0e3d901cf6274873fa9b750c10256c09e2b954a2b595'

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User model definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    plate_number = db.Column(db.String(20), nullable=False)

# Drop and recreate the 'users' table
with app.app_context():
    db.create_all()

# Welcome page route
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Login page route
@app.route('/login')
def login():
    return render_template('login.html')

# Login form submission route
@app.route('/login', methods=['POST','GET'])
def login_submit():
    if request.method == 'POST':
        #handle form submission
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            return redirect(url_for('dashboard'))
        else:
            #handle get request
            return render_template('login.html', error='Invalid credentials')

# Signup form submission route
# Signup form submission route
# Signup form submission route
@app.route('/signup', methods=['GET', 'POST'])
def signup_submit():
    if request.method == 'POST':
        # Handle form submission
        username = request.form['username']
        email = request.form['email']

        # Check if username or email already exists in the database
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

        if existing_user:
            # If username or email already exists, render signup form with error message
            error = "Username or email already exists. Please choose a different one."
            return render_template('signup.html', error=error)
        else:
            # If username and email are unique, proceed with user registration
            password = generate_password_hash(request.form['password'])
            phone_number = request.form['phone_number']
            plate_number = request.form['plate_number']

            new_user = User(username=username, password=password, email=email, phone_number=phone_number, plate_number=plate_number)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))
    else:
        # Handle GET request (display signup form)
        return render_template('signup.html')


# Protected dashboard route
@app.route('/home')
def dashboard():
    return render_template('home.html')

# Other page routes (myparking, profile, more)
@app.route('/myparking')
def myparking():
    return render_template('myparking.html')

@app.route('/bookparking')
def bookparking():
    return render_template('bookparking.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))  # Redirect to the login page if the user is not logged in

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        token = request.form['token']

        # Process payment based on the selected payment method
        if payment_method == 'visa':
            # Process Visa payment
            # You can implement your Visa payment logic here
            return redirect(url_for('payment_success'))
        elif payment_method == 'ecocash':
            # Process Ecocash payment
            # You can implement your Ecocash payment logic here
            # For demonstration, let's redirect to a success page
            return redirect(url_for('payment_success'))
    else:
        # Handle GET request (display payment page)
        fake_token = str(uuid.uuid4())
        return render_template('payment.html', fake_token=fake_token)

@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')


if __name__ == '__main__':
    app.run(debug=True)
