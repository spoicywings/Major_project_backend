import pytest
import requests
import json
import time

from src import config
from src.error import InputError, AccessError
from datetime import datetime

BASE_URL = config.url

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

@pytest.fixture
def standup_create():
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'length': 2
    })

# Raises an AccessError when token is invalid
def test_invalid_token(clear_data, standup_create):
    response = requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 
        'channel_id': 1,
        'message': "hi"
    })
    
    assert response.status_code == AccessError.code

# Raises an InputError when channel_id is invalid
def test_invalid_channel_id(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'length': 2
    })

    response = requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 2,
        'message': "hi"
    })
    
    assert response.status_code == InputError.code

# Raises an InputError when message over 1000 characters
def test_over_1000_message(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'length': 2
    })
    
    response = requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'message': "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na"
    })
    
    assert response.status_code == InputError.code

# Raises an InputError when there is not an active standup
def test_active_standup(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    response = requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'message': "hi"
    })
    
    assert response.status_code == InputError.code

# Raises an AccessError when channel_id is valid but not member of channel
def test_not_channel_member(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'length': 2
    })
    
    response = requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user2_data['token'], 
        'channel_id': 1,
        'message': "hi"
    })
    
    assert response.status_code == AccessError.code
    
# When standup_send is successful with one user
def test_standup_send_successful_one_user(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'length': 2
    })
    
    requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'message': "hi"
    })
    
    time.sleep(2)
    
    response = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'start': 0
    })
    response_data = response.json()
    
    assert response_data['messages'][0]['message'] == "joebrown: hi"

# When standup_send is successful with multiple users
def test_standup_send_successful_multiple_users(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()
    
    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joewsmith@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user2_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user1_data['token'],
        'channel_id': 1
    })
    
    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user2_data['token'], 
        'channel_id': 1,
        'length': 2
    })
    
    requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user2_data['token'], 
        'channel_id': 1,
        'message': "hi"
    })
    
    requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'message': "hey"
    })
    
    time.sleep(2)
    
    response = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user2_data['token'], 
        'channel_id': 1,
        'start': 0
    })
    response_data = response.json()
    
    assert response_data['messages'][0]['message'] == "johnsmith: hi\njoebrown: hey"
