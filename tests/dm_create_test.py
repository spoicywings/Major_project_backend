import pytest
import requests

from src import config
from src.auth import auth_register_v1
from src.data_store import data_store
from src.other import clear_v1

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

@pytest.fixture
def register_single():
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })

@pytest.fixture
def register_multiple():
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })

# Raises an AccessError.code when token is invalid
def test_invalid_token(clear_data, register_single):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })

    response = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw',
        'u_ids': [1]
    })
    
    assert response.status_code == AccessError.code

# Raises an InputError.code when u_ids contains a u_id that is invalid
def test_invalid_uids(clear_data, register_single):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })

    response_data = response.json()

    response = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [1, 3]
    })
    
    assert response.status_code == InputError.code

# Raises an AccessError.code when both token and u_ids are invalid
def test_both_invalid_token_uids(clear_data, register_single):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })

    response = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw',
        'u_ids': [1, 2, 3]
    })
    
    assert response.status_code == AccessError.code

# Sucessful return should store new DM in data store
def test_dm_created_two_users(clear_data, register_single):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })

    response_data = response.json()

    response = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [1]
    })
    
    response_data = response.json()
    
    assert response_data['dm_id'] == 1

# Test for multiple users in a DM
def test_dm_created_multiple_users(clear_data, register_multiple):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'tonybrown@gmail.com', 'password': 'comp1531', 
        'name_first': 'Tony', 'name_last': 'Brown'
    })

    response_data = response.json()

    response = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [1, 2, 3]
    })
    
    response_data = response.json()
    
    assert response_data['dm_id'] == 1

# Test that multiple DMs can be created
def test_two_dms_created(clear_data, register_single):
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })

    response_data = response.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [1]
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'tonybrown@gmail.com', 'password': 'comp1531', 
        'name_first': 'Tony', 'name_last': 'Brown'
    })
    
    response = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [3, 4]
    })
    
    response_data = response.json()
    
    assert response_data['dm_id'] == 2
