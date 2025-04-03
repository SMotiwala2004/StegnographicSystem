from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config.db import db
from models.user import User
from routes.auth_routes import auth_bp
import os

app = Flask(__name__)

# Configuration

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'postgresql://your_user:your_password@localhost:5432/your_database')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialize Extensions

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

# Register Blueprints

app.register_blueprint(auth_bp, url_prefix='/auth')

# Create Database Tables

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)