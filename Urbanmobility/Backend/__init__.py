import click
from flask import Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
static_dir = os.path.join(template_dir, 'public')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
api = Api(app)


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app) 
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from Urbanmobility.Backend import routes

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")


# names = {
#     "John": {"age": 20, "gender": "male"},
#     "Jane": {"age": 21, "gender": "female"},
#     "Jim": {"age": 22, "gender": "male"},
# }
# class HelloWorld(Resource):
#     def get(self, name):
#         return names[name]

# api.add_resource(HelloWorld, '/helloworld/<string:name>')



@app.cli.command()
@click.option('--username', default='admin', help='The username for the admin user')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password for the admin user')
def create_admin(username, password):
    from Urbanmobility.Backend.models import User

    with app.app_context():
        if User.query.filter_by(username=username).first():
            click.echo('User already exists!')
            return
        
        hashed_pwd = bcrypt.generate_password_hash(password).decode('utf-8')
        admin_user = User(username=username, password=hashed_pwd)
        db.session.add(admin_user)
        db.session.commit()
        click.echo(f'Admin user "{username}" created successfully!')

    
    if User.query.filter_by(username=username).first():
        print(f"User '{username}' already exists.")
    else:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin_user = User(username=username, password=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")