from src.data_store import data_store
from src.error import InputError
from src.other import decode_jwt, check_valid_token
from src import config

from PIL import Image
from os import path
import urllib.request
import sys
import os
import jwt
import re

BASE_URL = config.url

def user_profile_v1(token, u_id):
    '''
    For a valid user, returns information about their 
    user_id, email, first name, last name and handle

    Arguments:
        token (string),
        u_id (int)
    
    Exceptions:
        InputError - when u_id does not refer to a valid user
    
    Return value:
        { user }
    '''    
    
    # Check valid token        
    check_valid_token(token)
    
    store = data_store.get()    

    valid_user = False  

    # Check if u_id refers to a valid user, otherwise raise InputError
    for user in store['users']:
        if user['u_id'] == u_id:
            valid_user = True
            break
    
    if valid_user == False:
        raise InputError(description="Invalid User ID")
        
    return {
        'u_id': user['u_id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str'],
        'profile_img_url': user['profile_img_url']
    }

def user_profile_setname_v1(token, name_first, name_last):
    '''
    For a valid user, returns information about their 
    user_id, email, first name, last name and handle

    Arguments:
        token (string),
        u_id (int)
    
    Exceptions:
        InputError - when u_id does not refer to a valid user
    
    Return value:
        { user }
    '''
    
    decoded_token = check_valid_token(token)
    store = data_store.get()
    
    # Get the user
    for user in store['users']:
        if user['u_id'] == decoded_token['u_id']:
            # Check if new first name is valid
            if len(name_first) < 1 or len(name_first) > 50:
                raise InputError(description="First name must be between 1 to 50 characters")
            else:
                user['name_first'] = name_first
                
            # Check if new last name is valid
            if len(name_last) < 1 or len(name_last) > 50:
                raise InputError(description="Last name must be between 1 to 50 characters")
            else:
                user['name_last'] = name_last
    
    data_store.set(store)

    return {
    }    

def user_profile_setemail_v1(token, email):
    '''
    Update the authorised user's email address

    Arguments:
        token (string),
        email (string)
    
    Exceptions:
        InputError - when email entered is not a valid email
        InputError - email address is already being used by another user
    
    Return value:
        {  }
    '''
    
    decoded_token = check_valid_token(token)
    store = data_store.get()
    
    # A valid email should match this expression
    valid = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not(re.fullmatch(valid, email)):
        raise InputError(description="Invalid email")
    
    # Check if email is already in use
    for user in store['users']:
        if user['email'] == email:
            raise InputError(description="Email already in use")
            
    # Get the user   
    for user in store['users']:
        if user['u_id'] == decoded_token['u_id']:
            # Change the user's email
            user['email'] = email
    
    data_store.set(store)         
            
    return {
    }
    
def user_profile_sethandle_v1(token, handle_str): 
    '''
    Update the authorised user's handle (i.e. display name)

    Arguments:
        token (string),
        handle_str (string)
    
    Exceptions:
        InputError - when length of handle_str is not between 3 and 20 characters inclusive
        InputError - when handle_str contains characters that are not alphanumeric
        InputError - when the handle is already used by another user
    
    Return value:
        {  }
    '''
    
    decoded_token = check_valid_token(token)
    store = data_store.get()
    
    # Check if new display name is within the required length
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description="Display name must be between 3 to 20 characters")
    
    # Check if new display name contains non alphanumeric characters
    if handle_str.isalnum() == False:
        raise InputError(description="Display name must be alphanumeric only")
        
    # Check if the display name is already taken
    for user in store['users']:
        if user['handle_str'] == handle_str:
            raise InputError(description="Display name is already taken")
    
    # Change the users display name
    for user in store['users']:
        if user['u_id'] == decoded_token['u_id']: 
            user['handle_str'] = handle_str

    data_store.set(store)
    
    return {
    }
    
def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Given a URL of an image on the internet, crops the image within bounds 
    (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left. 
    
    Arguments:
        token (string)
        img_url (string)
        x_start (integer)
        y_start (integer)
        x_end (integer)
        y_end (integer)
        
    Exceptions:
        InputError - when img_url returns an HTTP status other than 200
        InputError - when any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
        InputError - when x_end is less than x_start or y_end is less than y_start
        InputError - when image uploaded is not a JPG
        
    Return value:
        {  }    
    '''
    
    # Check valid token
    user_data = check_valid_token(token)
    u_id = user_data['u_id']
    
    store = data_store.get()
    
    valid_img_format = ['jpg', 'jpeg']
    
    # Check if image is a JPG, otherwise raise InputError
    if img_url.split('.')[-1] not in valid_img_format:
        raise InputError(description="Image must be a JPG")
        
    # Create a filename for the user profile image (file path)      
    directory = os.getcwd() + '/src/static'
    filename = directory + '/' + str(u_id) + '.jpg'

    try:
        urllib.request.urlretrieve(img_url, filename)    
    except:
        raise InputError(description="Invalid HTTP status") from InputError
    
    # Check that the given dimensions are valid
    check_valid_dimensions(filename, x_start, y_start, x_end, y_end)
    
    # Crop the image
    img = Image.open(filename)
    cropped = img.crop((x_start, y_start, x_end, y_end))
    cropped.save(filename)
    
    # Save the url of the image
    profile_img_url = f'{BASE_URL}static/{u_id}.jpg'
    
    # Change the user's profile img url
    for user in store['users']:
        if user['u_id'] == user_data['u_id']:
            user['profile_img_url'] = profile_img_url
            
    data_store.set(store)
        
    return {
    }
    
# user/profile/uploadphoto helper functions  
def check_valid_dimensions(filename, x_start, y_start, x_end, y_end):
    img = Image.open(filename)

    # Check if x_end is less than x_start or y_end is less than y_start
    if x_end < x_start:
        raise InputError(description="x_end cannot be less than x_start")
        
    if y_end < y_start:
        raise InputError(description="y_end cannot be less than y_start")
        
    # Check if any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL 
    width, height = img.size
    if x_start < 0 or x_start > width:
        raise InputError(description="x_start not within dimensions of the image")
        
    if y_start < 0 or y_start > height:
        raise InputError(description="y_start not within dimensions of the image")
        
    if x_end < 0 or x_end > width:
        raise InputError(description="x_end not within dimensions of the image")
        
    if y_end < 0 or y_end > height:
        raise InputError(description="y_end not within dimensions of the image")
        
    return {
    }
      
