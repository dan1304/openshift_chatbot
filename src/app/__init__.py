from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from urllib.parse import quote  

app = Flask(__name__, template_folder='../templates/')

db_password = quote("P@ss99W0rd")
db_url = "dev-master-db.ascendmoney-dev.internal"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://chatbot:{db_password}@{db_url}:3306/chatbot_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from kbs import models
