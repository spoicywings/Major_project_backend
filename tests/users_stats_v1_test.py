import pytest
import requests
import json
import time

from src import config
from src.error import AccessError

BASE_URL = config.url

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def test_invalid_token(clear_data):
    # Register one user
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    })
    
    # Pass in invalid token
    response = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw'
    })
    
    assert response.status_code == AccessError.code
    
def test_initial_users_stats_successful(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 0
    assert response_data['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 0
    assert response_data['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0
    assert response_data['workspace_stats']['utilization_rate'] == 0
    
def test_correct_channels_exist_stat(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': False
    })
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 1
    assert response_data['workspace_stats']['utilization_rate'] == 1
    
def test_correct_dms_exist_stat(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a dm
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': []
    })
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 1
    assert response_data['workspace_stats']['utilization_rate'] == 1

def test_correct_dms_exist_after_removing_dm(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a dm
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': []
    })
    
    # Remove the dm
    requests.delete(BASE_URL + 'dm/remove/v1', json = {'token': user_data['token'], 'dm_id': 1})
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 0
    
def test_correct_messages_exist_stat(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': False
    })
    
    # Send a message in the channel
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_data['token'],
        'channel_id': 1,
        'message': 'Hello'
    })
    
    # Create a dm
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': []
    })
    
    # Send a message in the dm
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_data['token'],
        'dm_id': 1,
        'message': "hi"
    })
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 2
    
def test_correct_messages_exist_after_removing_message(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': False
    })
    
    # Send a message in the channel
    message_data = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_data['token'],
        'channel_id': 1,
        'message': 'Hello'
    }).json()
    
    # Delete the message
    requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_data['token'],
        'message_id': message_data['message_id']
    })
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0

def test_correct_messages_exist_after_standup(clear_data): 
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': False
    })
    
    # Start a standup
    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user_data['token'], 
        'channel_id': 1,
        'length': 2
    })
        
    # Send a message in the standup
    requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user_data['token'], 
        'channel_id': 1,
        'message': "hi"
    })
    
    time.sleep(2)
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 1
    
def test_correct_msgs_exist_after_removing_dm(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': False
    })
    
    # Send a message in the channel
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_data['token'],
        'channel_id': 1,
        'message': 'Hello'
    })
    
    # Create a dm
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': []
    })
    
    # Send a message in the dm
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_data['token'],
        'dm_id': 1,
        'message': "hi"
    })
    
    # Remove the dm
    requests.delete(BASE_URL + 'dm/remove/v1', json = {
        'token': user_data['token'], 'dm_id': 1
    })
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 1
    
def test_correct_utilization_rate(clear_data):
    # Register two users
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    # First user creates a channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': False
    })
    
    # First user creates a dm with no one else in it
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': []
    })
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['utilization_rate'] == 1/2

def test_correct_utilization_rate_after_removing_user(clear_data):
    # Register two users
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    
    # First user creates a channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': False
    })
    
    # Remove the first user
    requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user_data['token'],
        'u_id': 2,
    })
    
    # Call users/stats/v1
    response_data = requests.get(BASE_URL + 'users/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['workspace_stats']['utilization_rate'] == 1

    
