from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ - "users"

    id = db.column(db.Integer, primary_key = True)
    username = db.column(db.String(50), unique = True, nullable = False)
    password_hash = db.column(db.String(225), nullable = False)
    email = db.column(db.String(120), unique = True, nullable = False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        self.password_hash = check_password_hash(password)
