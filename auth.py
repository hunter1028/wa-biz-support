# -*- coding: utf-8 -*-

def do_auth(user_name, password):
    if user_name == 'admin' and password == 'admin':
        return True
    else:
        return False