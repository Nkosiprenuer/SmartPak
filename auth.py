from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
import hashlib

# Hash the secret key using SHA256
hashed_secret_key = hashlib.sha256(b'87b8e4b5-816f-40ba-871e-0e3d901cf6274873fa9b750c10256c09e2b954a2b595').hexdigest()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = hashed_secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///staff.db'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define SQLAlchemy models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Initialize Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

# Add views for SQLAlchemy models
admin.add_view(ModelView(User, db.session))

if __name__ == '__main__':
    with app.app_context():  # Ensures database creation within application context
        # Create database tables
        db.create_all()
    
    # Run the Flask app
    app.run(debug=True)