import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Get the absolute path of the project directory
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Configure the secret key and database URI
app.config['SECRET_KEY'] = 'a_very_secret_key_that_should_be_changed'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # The route to redirect to for login
login_manager.login_message_category = 'info'


# --- Database Models ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    # 'admin' or 'standard'
    role = db.Column(db.String(20), nullable=False, default='standard')
    simulations = db.relationship('Simulation', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class CorrectionFactor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Storing as 'jul/94' format
    month_year = db.Column(db.String(10), unique=True, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"CorrectionFactor('{self.month_year}', {self.value})"

class Simulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    benefit_type = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    result = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    salaries = db.relationship('SalaryContribution', backref='simulation', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Simulation(Server: '{self.server_name}', Result: {self.result})"

class SalaryContribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulation.id'), nullable=False)
    # Storing as 'jul/94' format
    month_year = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"SalaryContribution('{self.month_year}', {self.amount})"

# --- Flask-Login User Loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after app and db are defined to avoid circular imports
from app import routes
