import pytest
import requests

import json
from src import config

BASE_URL = config.url

from src.error import InputError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def test_invalid_setemail_no_at(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()

    # Try to set email with no '@'
    response = requests.put(BASE_URL + 'user/profile/setemail/v1', json = {
        'token': login_data['token'], 'email': 'invalidemail.com'
    })
    
    assert response.status_code == InputError.code
    
def test_invalid_setemail_with_at(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Try to set email with unusable character '!'
    response = requests.put(BASE_URL + 'user/profile/setemail/v1', json = {
        'token': login_data['token'], 'email': '!@email.com'
    })
    
    assert response.status_code == InputError.code
    
def test_invalid_setemail_too_many_ats(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Try to set email with too many '@'
    response = requests.put(BASE_URL + 'user/profile/setemail/v1', json = {
        'token': login_data['token'], 'email': 'thisis@invalid@email.com'
    })
    
    assert response.status_code == InputError.code
    
def test_invalid_setemail_no_domain(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Try to set email with no domain 
    response = requests.put(BASE_URL + 'user/profile/setemail/v1', json = {
        'token': login_data['token'], 'email': 'invalid@emailcom'
    })
    
    assert response.status_code == InputError.code
    
def test_setemail_email_already_exists(clear_data):
    # Register multiple users
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid2@email.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    # Login
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Try to set email to one already in use
    response = requests.put(BASE_URL + 'user/profile/setemail/v1', json = {
        'token': login_data['token'], 'email': 'valid2@email.com'
    })
    
    assert response.status_code == InputError.code
    
def test_setemail_valid(clear_data):
    # Register one user (John Smith)
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    # Register another user (Bill Billy)
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password', 
        'name_first': 'Bill', 'name_last': 'Billy'
    })
    
    # Login with John Smith
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Change email
    requests.put(BASE_URL + 'user/profile/setemail/v1', json = {
        'token': login_data['token'], 'email': 'johnsmith@gmail.com'
    })
     
    # Get John Smith's user profile
    response = requests.get(BASE_URL + 'user/profile/v1', params = {
        'token': login_data['token'], 'u_id': login_data['auth_user_id']
    })
    
    response_data = response.json()

    # Assert that email has changed
    assert response_data['user']['email'] == 'johnsmith@gmail.com'
    
    
