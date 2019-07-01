#-*- coding: utf-8 -*-
'''
ibm_dist.view.login -- watson assistant biz support

@author:     IBM
@copyright:  2019 IBM distribution. All rights reserved.
@version: 1.0

Created on 2019/06/26
'''

from flask import Blueprint, redirect, request, url_for, render_template, make_response, jsonify
from flask_login import login_user, logout_user, login_required
from ibm_dist.utils.user_authorization import User, do_auth
from flask_api import status

url = Blueprint('login', __name__)

@url.route('/')
def index():
    return render_template('login.html')

@url.route('/login', methods=['POST', 'GET'])
def login():
    logout_user()
    user_name = request.args.get('username', None)
    password =  request.args.get('password', None)
    remember_me = request.args.get('rememberme', False)
    if user_name == '' or  password == '':
        result = {'MASSAGE' : 'Username or Password is required!'}
        return make_response(jsonify(result), status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        
    user = User(user_name)
    
    if user.verify_password(password):
        login_user(user, remember=remember_me)
        return render_template('index.html')
    else:
#         flash('Wrong username or password!')
#         next = request.args.get('next')
#         return redirect(next or url_for('login.index'))
        result = {'MASSAGE' : 'Username or Password verification failed!'}
        return make_response(jsonify(result), status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

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


