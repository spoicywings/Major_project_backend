import pytest
import requests

from src import config

BASE_URL = config.url

from src.error import AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def test_logout_correctly(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Logout
    response = requests.post(BASE_URL + 'auth/logout/v1', json = {
        'token': login_data['token']
    })
  
    assert response.status_code == 200
   
def test_logout_after_multiple_logins(clear_data):
    # Register two users
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    # Simulate logging in on different devices with one user
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'new@email.com', 'password': 'password'
    })
    
    requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'new@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Logout on one device
    requests.post(BASE_URL + 'auth/logout/v1', json = {
        'token': login_data['token']
    })
    
    # logout again
    response = requests.post(BASE_URL + 'auth/logout/v1', json = {
        'token': login_data['token']
    })
    
    assert response.status_code == AccessError.code
            
def test_check_invalid_token(clear_data):  
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })    
    
    requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'new@email.com', 'password': 'password'
    })
    
    # Pass in an invalid token
    response = requests.post(BASE_URL + 'auth/logout/v1', json = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiNyIsInNlc3Npb25faWQiOiIyMiJ9.yXar5yT57czwJYYqygt_uOFUk5Gz_N-MD1Jz6ghKFCw'
    })
    
    assert response.status_code == AccessError.code
