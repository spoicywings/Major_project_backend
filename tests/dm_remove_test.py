import pytest
import requests
import json

from src import config

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

@pytest.fixture
def dm_create_single():
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })

    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })

    response_data = response.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [1]
    })

# Raises an AccessError.code when token is invalid
def test_invalid_token(clear_data, dm_create_single):
    response = requests.delete(BASE_URL + 'dm/remove/v1', json = {'token': 
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 'dm_id': 1})
    
    assert response.status_code == AccessError.code

# Raises an InputError.code when dm_id is invalid
def test_invalid_dm_id(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    response_data = response.json()
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1]})

    response = requests.delete(BASE_URL + 'dm/remove/v1', json = {'token': response_data['token'], 'dm_id': 2})

    assert response.status_code == InputError.code

# Raises an AccessError.code when token and dm_id are invalid
def test_both_invalid_token_dm_id(clear_data, dm_create_single):
    response = requests.delete(BASE_URL + 'dm/remove/v1', json = {'token': 
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 'dm_id': 2})
    
    assert response.status_code == AccessError.code

# Raises an AccessError.code when a member of DM who is not the owner attempts to remove the DM
def test_not_owner(clear_data):
    data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    response_data = response.json()
    response = requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1]})

    response_data = response.json()
    
    not_owner = data.json()
    response = requests.delete(BASE_URL + 'dm/remove/v1', json = {'token': not_owner['token'], 'dm_id': response_data['dm_id']})

    assert response.status_code == AccessError.code

# Removal of DM is successful when the owner removes it
def test_owner_remove_dm(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    response_data = response.json()
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1]})

    requests.delete(BASE_URL + 'dm/remove/v1', json = {'token': response_data['token'], 'dm_id': 1})
    
    response = requests.get(BASE_URL + 'dm/list/v1', params = {'token': response_data['token']})
    response_data = response.json()
    
    assert response_data['dms'] == []
