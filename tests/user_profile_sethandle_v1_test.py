import pytest
import requests

import json
from src import config

BASE_URL = config.url

from src.error import InputError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def test_handle_length_too_short(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/sethandle/v1', json = {
        'token': login_data['token'], 'handle_str': 'hi'
    })
    
    assert response.status_code == InputError.code
    
def test_handle_length_too_long(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/sethandle/v1', json = {
        'token': login_data['token'], 'handle_str': 'aaaaaaaaaaaaaaaaaaaaa'
    })
    
    assert response.status_code == InputError.code
    
def test_handle_not_alphanumeric(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/sethandle/v1', json = {
        'token': login_data['token'], 'handle_str': '!@%$'
    })
    
    assert response.status_code == InputError.code
    
def test_handle_already_taken(clear_data):
    # Register two users with two different handles
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'abc', 'name_last': 'def'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'different@email.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/sethandle/v1', json = {
        'token': login_data['token'], 'handle_str': 'johnsmith'
    })
    
    assert response.status_code == InputError.code

def test_sethandle_valid(clear_data):
    # Register two users with two different handles
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'valid@email.com', 'password': 'password', 
        'name_first': 'Bill', 'name_last': 'Billy'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'different@email.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'valid@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/sethandle/v1', json = {
        'token': login_data['token'], 'handle_str': 'notBillBilly'
    })
    
    assert response.status_code == 200
