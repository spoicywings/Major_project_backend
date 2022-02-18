import pytest
import requests

import json
from src import config

BASE_URL = config.url

from src.error import InputError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

def test_first_name_too_short(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/setname/v1', json = {
        'token': login_data['token'], 'name_first': '', 'name_last': 'def'
    })
    
    assert response.status_code == InputError.code

def test_first_name_too_long(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/setname/v1', json = {
        'token': login_data['token'], 
        'name_first': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 
        'name_last': 'def'
    })
    
    assert response.status_code == InputError.code

def test_last_name_too_short(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/setname/v1', json = {
        'token': login_data['token'], 'name_first': 'abc', 'name_last': ''
    })
    
    assert response.status_code == InputError.code

def test_last_name_too_long(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/setname/v1', json = {
        'token': login_data['token'], 
        'name_first': 'abc', 
        'name_last': 'ddddddddddddddddddddddddddddddddddddddddddddddddddd'
    })
    
    assert response.status_code == InputError.code
    
def test_setname_valid(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'random@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'random@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    response = requests.put(BASE_URL + 'user/profile/setname/v1', json = {
        'token': login_data['token'], 
        'name_first': 'John', 
        'name_last': 'Smith'
    })
    
    assert response.status_code == 200

