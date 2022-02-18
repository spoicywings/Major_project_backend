import pytest
import requests

import json
from src import config

BASE_URL = config.url

from src.error import AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def test_invalid_token(clear_data):
    # Register and login
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'user1@email.com', 'password': 'password'
    })
    
    # Pass in an invalid token
    response = requests.get(BASE_URL + 'users/all/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw'
    })
    
    assert response.status_code == AccessError.code

def test_usersall_correct_return(clear_data):
    # Register multiple users
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    })
    
    # Login with first user
    login = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'user1@email.com', 'password': 'password'
    })
    
    login_data = login.json()
    
    # Get all users
    response = requests.get(BASE_URL + 'users/all/v1', params = {
        'token': login_data['token']
    })
    
    response_data = response.json()
    
    assert response_data['users'][1]['u_id'] == 2
    assert response_data['users'][1]['email'] == 'user2@email.com'
    assert response_data['users'][1]['name_first'] == 'Bill'
    assert response_data['users'][1]['name_last'] == 'Billy'
    assert response_data['users'][1]['handle_str'] == 'billbilly'

def test_usersall_removed_user(clear_data):
    # Register multiple users
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    })
    
    # Login with both users
    user1 = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'user1@email.com', 'password': 'password'
    })
    
    user2 = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'user2@email.com', 'password': 'password'
    })
    
    user1_data = user1.json()
    user2_data = user2.json()
    
    # User1 promotes user2 to global owner
    requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1_data['token'],
        'u_id': user2_data['auth_user_id'],
        'permission_id': 1,
    })

    # Remove the second user (Bill Billy)
    requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user1_data['token'],
        'u_id': user2_data['auth_user_id']
    })
    
    # Get all users
    response = requests.get(BASE_URL + 'users/all/v1', params = {
        'token': user1_data['token']
    })
    
    response_data = response.json()
    
    # Assert that only one user is returned
    assert len(response_data['users']) == 1
    
