import pytest
import requests

import json
from src import config

from src.other import decode_jwt

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
 
def test_register_invalid_email_no_at(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'invalidgmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    assert response.status_code == InputError.code

def test_register_invalid_email_with_at(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': '!@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    assert response.status_code == InputError.code
    
def test_register_invalid_email_too_many_ats(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'thisis@invalid@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    assert response.status_code == InputError.code
    
def test_register_invalid_email_no_domain(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'invalid@gmailcom', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    assert response.status_code == InputError.code
    
def test_register_duplicate_email(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
                                                                    
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    assert response.status_code == InputError.code

def test_register_invalid_password(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'abc', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    assert response.status_code == InputError.code
    
def test_register_firstname_too_short(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': '', 'name_last': 'Gush'
    })  
    
    assert response.status_code == InputError.code
    
def test_register_firstname_too_long(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Thisfirstnameislongerthan50charactersandisthusinvalid', 'name_last': 'Gush'
    })
    
    assert response.status_code == InputError.code
                                                                    
def test_register_lastname_too_short(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': ''
    })
    
    assert response.status_code == InputError.code
    
def test_register_lastname_too_long(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Thislastnameislongerthan50charactersandisthusinvalid'
    })
    
    assert response.status_code == InputError.code
    

def test_register_check_valid_id(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    response_data = response.json()
    assert response_data['auth_user_id'] == 1
    
def test_register_check_multiple_valid_id(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
     })
                                                                    
    response2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'newemail@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })            
                                                        
    response_data = response.json()
    response2_data = response2.json()
    
    assert response_data['auth_user_id'] == 1
    assert response2_data['auth_user_id'] == 2
              
def test_decoded_jwt(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    response_data = response.json()
    
    assert decode_jwt(response_data['token'])['u_id'] == 1
            
def test_different_decoded_token_returns(clear_data):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    response2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    response_data = response.json()
    response2_data = response2.json()
    
    assert decode_jwt(response_data['token'])['u_id'] != decode_jwt(response2_data['token'])['u_id']
    assert decode_jwt(response_data['token'])['session_id'] != decode_jwt(response2_data['token'])['session_id']
    
def test_valid_auth_register(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    assert response.status_code == 200


            
