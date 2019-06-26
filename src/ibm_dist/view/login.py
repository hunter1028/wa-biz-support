# -*- coding: utf-8 -*-
'''
Created on 2019/06/26
@author: leon by ibm distribution
'''

from flask import Blueprint, redirect, request, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required
from ibm_dist.user_authorization import User, do_auth

url = Blueprint('login', __name__)

@url.route('/')
def index():
#    return app.send_static_file('login.html')
#    return app.send_static_file('login2.html')
    return render_template('login.html')

@url.route('/login', methods=['POST', 'GET'])
def login():
    logout_user()
    user_name = request.args.get('username', None)
    password =  request.args.get('password', None)
    remember_me = request.args.get('rememberme', False)
    if user_name == '' or  password == '':
        return redirect('/')
        
    user = User(user_name)
    
    if do_auth(user_name, password):
        login_user(user, remember=remember_me)
        return render_template('index.html')
        # return redirect(url_for('/chatbot'))
    else:
        flash('Wrong username or password!')
        next = request.args.get('next')
        return redirect(next or url_for('index'))
    # return app.send_static_file('index.html')
    # return redirect('/index')

# csrf protection
# csrf = CSRFProtect()
# csrf.init_app(app)

@url.route('/chatbot', methods=['POST', 'GET'])
@login_required
def chatbot():
    return render_template('index.html')

@url.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.referrer or url_for('/'))



