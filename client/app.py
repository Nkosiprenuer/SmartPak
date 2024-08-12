from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Increased length to accommodate hashed passwords

# Create the database tables
with app.app_context():
    db.create_all()

# Route for the welcome page
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Route for the login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route for handling login form submission
@app.route('/login', methods=['POST'])
def login_submit():
    # Handle login form submission
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user and pbkdf2_sha256.verify(password, user.password):
        # Successful login, redirect to welcome page
        return render_template('home.html')
    else:
        # Incorrect credentials, render login page with error message
        return render_template('login.html', error=True)

# Route for the signup page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Route for handling signup form submission
@app.route('/signup', methods=['POST'])
def signup_submit():
    # Handle signup form submission
    username = request.form['username']
    password = request.form['password']
    
    # Hash the password before storing it
    hashed_password = pbkdf2_sha256.hash(password)
    
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    # Redirect to the welcome page after signup
    return redirect(url_for('welcome'))

# Routes for other pages (myparking, profile, more)
@app.route('/myparking')
def myparking():
    return render_template('myparking.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/more')
def more():
    return render_template('more.html')

if __name__ == '__main__':
    app.run(debug=True)
