import pytest
import requests

from src import config
from src.other import decode_jwt

BASE_URL = config.url

from src.error import InputError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def test_login_unregistered(clear_data):
    response = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    assert response.status_code == InputError.code
    
    
def test_login_unknown_email(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    response = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'different@email.com', 'password': 'password'
    })
    
    assert response.status_code == InputError.code
    

def test_login_incorrect_password(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    response = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'wrongpassword'
    })
    
    assert response.status_code == InputError.code
    
    
def test_login_correct_user_id(clear_data):
    # Register one user and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    # Register another user and login
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@email.com', 'password': 'password',
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    login_response = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'john@email.com', 'password': 'password'
    })
    
    register_response_data = register_response.json()
    login_response_data = login_response.json()
    
    assert register_response_data['auth_user_id'] == login_response_data['auth_user_id']
    
    
def test_login_same_token_email(clear_data):
    # Register a user and login
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login_response = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    register_response_data = register_response.json()
    login_response_data = login_response.json()
    
    # Assert that email used in token generation is the same
    assert decode_jwt(register_response_data['token'])['u_id'] == decode_jwt(login_response_data['token'])['u_id']
        

def test_login_different_tokens(clear_data):
    # Register a user and login
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })

    login_response = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    register_response_data = register_response.json()
    login_response_data = login_response.json()
    
    # Assert that tokens generated are different, due to different session ids
    assert register_response_data['token'] != login_response_data['token']
