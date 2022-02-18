from src.data_store import data_store
from src.error import InputError
from src.other import hashing, generate_session_id, create_jwt, decode_jwt, check_valid_token, reaction_current_user
from src import config

from datetime import datetime, timezone

import hashlib
import jwt
import random
import smtplib

from os import path
import sys
import os

import re

SECRET = 'F13BCAMEL'
BASE_URL = config.url

def auth_login_v1(email, password):

    '''
    Given a registered user's email and password, returns their 'token' value

    Arguments:
        - email (string),
        - password (string)

    Exceptions:
        InputError - when email entered does not belong to a user
        InputError - password is not correct

    Return value:
        { token, auth_user_id }
    '''         
    
    store = data_store.get()
    
    valid_email = False
    valid_password = False
    
    # Check if email is registered
    for user in store['users']:
        if user['email'] == email:
            valid_email = True
            break
    
    # If email is not registered, raise InputError
    if valid_email == False:
        raise InputError(description="This email is not registered")
    
    # Check if password is correct
    else:
        if user['password'] == hashing(password):
            valid_password = True
    
    # If password is incorrect
    if valid_password == False:
        raise InputError(description="Incorrect password")
        
    # If the user is registered (valid email and password), get their auth_user_id
    user_id = user['u_id']
    
    session_id = generate_session_id()
    user['session_id'].append(session_id)
    token = create_jwt(user_id, session_id)
    
    data_store.set(store)
    reaction_current_user(user_id)
    return {
        'auth_user_id': user_id,
        'token': token,
    }

def auth_register_v1(email, password, name_first, name_last):
    
    '''
    Given a user's first and last name, email address, and password, 
    create a new account for them and return a new `token`.

    Arguments:
        - email (string),
        - password (string),
        - name_first (string),
        - name_last (string)

    Exceptions:
        InputError - when email entered is not a valid email
        InputError - when email address is already being used by another user
        InputError - when length of password is less than 6 characters
        InputError - when length of name_first is not between 1 and 50 characters inclusive
        InputError - when length of name_last is not between 1 and 50 characters inclusive

    Return value:
        { token, auth_user_id }
    '''

    store = data_store.get()  
    session_list = [] 
    user_dict = {}
    
    # Create a new id for the user
    new_id = len(store['users']) + 1
    
    # A valid email should match this expression
    valid = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    
    # Check if the email is valid according to the above expression
    if not(re.fullmatch(valid, email)):
        raise InputError(description="Invalid email")
    
    # If the email is valid, check that it is not already taken    
    else: 
        for user in store['users']:
            if user['email'] == email:
                raise InputError(description="Email already in use")
                
        # If the email is not taken, add the email to the data store
        user_dict['email'] = email 
        
    # Check valid password
    if len(password) < 6:
        raise InputError(description="Invalid password, must be longer than 6 characters")
        
    else:
        user_dict['password'] = hashing(password)
    
    # Check valid first name
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="First name must be between 1 to 50 characters") 
        
    else:
        user_dict['name_first'] = name_first   
        
    # Check valid last name   
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="Last name must be between 1 to 50 characters")   
        
    else:
        user_dict['name_last'] = name_last   
    
    # Generate the handle 
    # Make first name and last name lowercase, and combine them
    new_string = name_first.lower() + name_last.lower()
    
    # Remove non-alphanumeric characters
    handle = re.sub(r'[^a-zA-Z0-9]', '', new_string)
    
    # If the handle is longer than 20 characters, cut it off at 20 characters
    handle = handle[:20]
    
    # If the handle is already taken, append the smallest number
    # (starting from 0) to form a new handle that isn't already taken
    counter = 0
    handle_len = len(handle)
    for user in store['users']:
        while handle in user['handle_str']:
            handle = handle[:handle_len] + str(counter)
            counter += 1
                       
    user_dict['handle_str'] = handle
    user_dict['u_id'] = new_id
    
    if new_id == 1:
        user_dict['global_owner'] = True
        user_dict['global_member'] = False
        
        # If the user is the first user registered, initialise the workplace_stats
        workspace_stats = {}

        timestamp = int(datetime.now(timezone.utc).timestamp())
        
        workspace_stats['channels_exist'] = [{'num_channels_exist': 0, 'time_stamp': timestamp}]
        workspace_stats['dms_exist'] = [{'num_dms_exist': 0, 'time_stamp': timestamp}]
        workspace_stats['messages_exist'] = [{'num_messages_exist': 0, 'time_stamp': timestamp}]
        workspace_stats['utilization_rate'] = 0
        
        store['stats'].append(workspace_stats)
        
    else:
        user_dict['global_owner'] = False
        user_dict['global_member'] = True
    
    # Create a new token using JWTs
    session_id = generate_session_id()
    session_list.append(session_id)
    user_dict['session_id'] = session_list
    token = create_jwt(new_id, session_id)
    
    # Set default profile image
    default_image = f'{BASE_URL}static/default.jpg'
        
    user_dict['profile_img_url'] = default_image

    # Create user stats dictionary and add to user data
    user_stats = {}
    
    timestamp = int(datetime.now(timezone.utc).timestamp())

    user_stats['channels_joined'] = [{'num_channels_joined': 0, 'time_stamp': timestamp}]
    user_stats['dms_joined'] = [{'num_dms_joined': 0, 'time_stamp': timestamp}]
    user_stats['messages_sent'] = [{'num_messages_sent': 0, 'time_stamp': timestamp}]
    user_stats['involvement_rate'] = 0
    
    user_dict['user_stats'] = user_stats
    
    # Create empty notifications for user
    user_dict['notifications'] = []
    
    # Append the user's data to the data store
    store['users'].append(user_dict)
    data_store.set(store)
    reaction_current_user(new_id)
    return {
        'auth_user_id': new_id,
        'token': token,
    }

def auth_logout_v1(token):

    '''
    Given an active token, invalidates the token to log the user out.

    Arguments:
        - token (string)

    Exceptions:
        N/A

    Return value:
        {  }
    '''

    # Check if the token is valid and return payload, otherwise raise AccessError
    decoded_token = check_valid_token(token)

    store = data_store.get()    
    
    # Get the user information from the decoded token
    user_id = decoded_token['u_id']
    user_session_id =  decoded_token['session_id']
    
    # Invalidate the token to log the user out
    for user in store['users']:
        if user['u_id'] == user_id and user_session_id in user['session_id']:
            user['session_id'].remove(user_session_id)
    
    data_store.set(store)
    
    return {
    }

def auth_passwordreset_request_v1(email): 

    ''' send an email containing a secret password reset code '''
    ''' use is logged out of all current sessions. '''  
    
    # Check if user is a registered user
    
    data = data_store.get()
    
    valid_email = False
    for user in data['users']:
        if user['email'] == email:
            valid_email = True
            user_id = user['u_id']
            break
            
    if valid_email == False:
        return {
        }       
    
     
    # Generate the 10 character secret code email with English alphabet ASCII
    secret_code = ''
    i = 0
    while i <= 10:
        
        # get integer value for uper and lowercase letters
        random_int = random.randint(97, 97 + 26 - 1)
        flip_case = random.randint(0,1)
        
        # if flip_case is 1, flip to lowercase
        if flip_case == 1:
            random_int = random_int - 32
            
        # append to string
        secret_code += (chr(random_int))
        i += 1
         
    # Store the secret code in data_store
    code_dict = {}
    code_dict['reset_code'] = secret_code
    code_dict['email'] = email
    data['codes'].append(code_dict)
    
      
    # Send the email
    gmail_user = 'comp1531camel@gmail.com'
    gmail_app_password = 'detail_digestion'
    sent_from = gmail_user
    sent_to = email
    sent_body = secret_code

    
       
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_app_password)
    server.sendmail(sent_from, sent_to, sent_body)
    server.close()
         
    
    # Log the user out
    data['users'][user_id - 1]['session_id'].clear()   
    data_store.set(data)
    
    
    return {
    }
    
def auth_passwordreset_reset_v1(reset_code, new_password):
    # Check if password is 6 or more characters
    if len(new_password) < 6:
        raise InputError(description="Password is less than 6 characters long")
    
    # Check if reset_code is valid
    data = data_store.get() 
    
    valid_code = False 
    code_email = ''  
    for code in data['codes']:
        if code['reset_code'] == reset_code:
            valid_code = True
            code_email = code['email']
            
    if valid_code == False:
        raise InputError(description="Invalid reset code")
    
    # Get user info
    for user in data['users']:
        if code_email == user['email']:
            user['password'] = hashing(new_password)
    
    data_store.set(data)    
    
    return {
    } 
    
    
    
