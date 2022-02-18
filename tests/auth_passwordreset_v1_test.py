import pytest
import requests
from src import config

BASE_URL = config.url

from src.error import InputError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def test_invalid_email(clear_data):
    ''' test the program does not raise an error due to security '''
    # Register User 1
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jimmy@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    response = requests.post(BASE_URL + 'auth/passwordreset/request/v1', json = {
        'email': 'john@gmail.com'
    })
    
    assert response.status_code == 200
        
def test_send_email(clear_data):  
    ''' test for sending email ''' 
        
    # Register User 1
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })

    response = requests.post(BASE_URL + 'auth/passwordreset/request/v1', json = {
        'email': 'john@gmail.com'
    })
    
    assert response.status_code == 200
    
def test_invalid_password(clear_data):
    ''' test giving an invalid password to password reset '''
    
    # give invalid password
    response = requests.post(BASE_URL + 'auth/passwordreset/reset/v1', json = {
        'reset_code': '', 'new_password': 'hi'
    })
    
    assert response.status_code == InputError.code
    
def test_invalid_code(clear_data):
    ''' test giving an invalid reset code '''
    
    # Register User 1
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })

    # Send code
    requests.post(BASE_URL + 'auth/passwordreset/request/v1', json = {
        'email': 'john@gmail.com'
    })
    
    # Test with invalid code
    response = requests.post(BASE_URL + 'auth/passwordreset/reset/v1', json = {
        'reset_code': 'a', 'new_password': 'validpassword'
    })
    
    assert response.status_code == InputError.code
