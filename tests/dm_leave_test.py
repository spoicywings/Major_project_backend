import pytest
import requests
import json

from src import config

BASE_URL = config.url

from src.error import InputError, AccessError
SUCCESS = 200

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
    response = requests.post(BASE_URL + 'dm/leave/v1', json = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw',
        'dm_id': 1
    })
    
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

    response = requests.post(BASE_URL + 'dm/leave/v1', json = {
        'token': response_data['token'],
        'dm_id': 2
    })

    assert response.status_code == InputError.code

# Raises an AccessError.code when token and dm_id are invalid
def test_both_invalid_token_dm_id(clear_data, dm_create_single):
    response = requests.post(BASE_URL + 'dm/leave/v1', json = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw',
        'dm_id': 2
    })
    
    assert response.status_code == AccessError.code

# Raises an AccessError.code when valid user is not member of DM
def test_not_member(clear_data, dm_create_single):
    not_member = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })
    
    not_member_data = not_member.json()
    response = requests.post(BASE_URL + 'dm/leave/v1', json = {
        'token': not_member_data['token'],
        'dm_id': 1
    })

    assert response.status_code == AccessError.code

# Test that when a member leaves the member no longer appears in dm_members
def test_member_leaves(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })

    member = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    member_data = member.json()
    
    owner = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })

    owner_data = owner.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': owner_data['token'],
        'u_ids': [1, 2]
    })

    requests.post(BASE_URL + 'dm/leave/v1', json = {
        'token': member_data['token'],
        'dm_id': 1
    })
    
    response = requests.get(BASE_URL + 'dm/details/v1', params = {'token': member_data['token'], 'dm_id': 1})
    
    assert response.status_code == AccessError.code

# Test that when owner leaves the owner no longer appears in dm_members/owner
# but the DM still exists and name is unchanged
def test_owner_leaves_name_unchanged(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })

    member = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    member_data = member.json()
    
    owner = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })

    owner_data = owner.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': owner_data['token'],
        'u_ids': [1, 2]
    })

    requests.post(BASE_URL + 'dm/leave/v1', json = {
        'token': owner_data['token'],
        'dm_id': 1
    })
    
    response = requests.get(BASE_URL + 'dm/details/v1', params = {'token': owner_data['token'], 'dm_id': 1})
    info = requests.get(BASE_URL + 'dm/details/v1', params = {'token': member_data['token'], 'dm_id': 1})
    
    info_data = info.json()
    
    assert response.status_code == AccessError.code
    assert info.status_code == SUCCESS
    assert info_data['name'] == "billjackson, eugenegush, johnsmith"
