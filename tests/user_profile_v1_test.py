import pytest
import requests

import json
from src import config

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

def test_invalid_user(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Pass in an invalid u_id
    response = requests.get(BASE_URL + 'user/profile/v1', params = {
        'token': login_data['token'], 'u_id': -1
    })
    
    assert response.status_code == InputError.code

def test_invalid_token(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'user1@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Pass in a different user token
    response = requests.get(BASE_URL + 'user/profile/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 
        'u_id': login_data['auth_user_id']
    })
    
    assert response.status_code == AccessError.code
    
def test_valid_user(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'user1@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Get the user profile
    response = requests.get(BASE_URL + 'user/profile/v1', params = {
        'token': login_data['token'], 'u_id': login_data['auth_user_id']
    })
    
    response_data = response.json()
    
    # Assert that all user details are correct
    assert response_data['user']['u_id'] == 1
    assert response_data['user']['email'] == 'user1@email.com'
    assert response_data['user']['name_first'] == 'abc'
    assert response_data['user']['name_last'] == 'def'
    assert response_data['user']['handle_str'] == 'abcdef'
    
    
    
