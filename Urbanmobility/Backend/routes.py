from flask import request, jsonify, render_template, flash, redirect, url_for
from Urbanmobility.Backend import app, db, bcrypt
from Urbanmobility.Backend.forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required

from Urbanmobility.Backend.models import User,Location,Vendor,Trip


# @app.route('/api/trips')
@app.route('/')
@app.route('/home')
@login_required 
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
                        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # next_page = request.args.get('next')
            flash('Login Successful!', 'success') 
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout ():
    logout_user()
    return redirect(url_for('home'))