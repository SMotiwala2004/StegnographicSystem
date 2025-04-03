from flask import Flask
from models import Model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db.init_app(app)

@app.route("/")
def hello_world():
    return "Hello, World!"