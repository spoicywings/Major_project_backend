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
    response = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw'
    })
    
    assert response.status_code == AccessError.code
    
def test_user_stats_successful(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['user_stats']['channels_joined'][-1]['num_channels_joined'] == 0
    assert response_data['user_stats']['dms_joined'][-1]['num_dms_joined'] == 0
    assert response_data['user_stats']['messages_sent'][-1]['num_messages_sent'] == 0
    assert response_data['user_stats']['involvement_rate'] == 0

def test_correct_return_type(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    response = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert type(response['user_stats']) == dict
    
def test_correct_channels_joined_stat(clear_data):
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
        
    # Call user/stats/v1
    response_data = response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1
    assert response_data['user_stats']['channels_joined'][-1]['time_stamp'] != None
    
def test_correct_dms_joined_stat(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a dm
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': [user_data['auth_user_id']]
    })
    
    # Call user/stats/v1
    response_data = response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1
    assert response_data['user_stats']['dms_joined'][-1]['time_stamp'] != None

def test_correct_messages_sent_stat(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a channel
    channel_data = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': True
    }).json()
    
    # Send a message in the channel
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_data['token'],
        'channel_id': channel_data['channel_id'],
        'message': 'Hello'
    })
    
    # Call user/stats/v1
    response_data = response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['user_stats']['messages_sent'][-1]['num_messages_sent'] == 1
    assert response_data['user_stats']['messages_sent'][-1]['time_stamp'] != None

def test_correct_involvement_rate_stat(clear_data):
    # Register two users
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    user2_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Eugene', 'name_last': 'Gush'
    }).json()
    
    # Create a channel
    channel_data = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': True
    }).json()
    
    # Send a message in the channel
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_data['token'],
        'channel_id': channel_data['channel_id'],
        'message': 'Hello'
    })
    
    # Create a dm
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': [user2_data['auth_user_id']]
    })
    
    # Call user/stats/v1
    response_data = response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    assert response_data['user_stats']['involvement_rate'] == 1
        
def test_num_channels_joined_after_leaving_channel(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a channel
    channel_data = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': True
    }).json()
    
    # Send multiple messages in the channel
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_data['token'],
        'channel_id': channel_data['channel_id'],
        'message': 'Hello'
    })
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_data['token'],
        'channel_id': channel_data['channel_id'],
        'message': 'I am Bill Billy'
    })
    
    # Leave channel
    requests.post(BASE_URL + 'channel/leave/v1', json = {
        'token': user_data['token'], 'channel_id': channel_data['channel_id']
    })

    # Call user/stats/v1
    response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
   
    assert response_data['user_stats']['channels_joined'][-1]['num_channels_joined'] == 0 
    assert response_data['user_stats']['messages_sent'][-1]['num_messages_sent'] == 2
    assert response_data['user_stats']['involvement_rate'] == 2/3
    
def test_num_channels_joined_after_inviting_user(clear_data):
    # Register two users
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    user2_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Eugene', 'name_last': 'Gush'
    }).json()
    
    # Create a channel
    channel_data = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': True
    }).json()
    
    # Invite the other user to the channel
    requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user_data['token'],
        'channel_id': channel_data['channel_id'],
        'u_id': user2_data['auth_user_id']
    })
    
    # Call user/stats/v1
    user2_response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user2_data['token']
    }).json()
    
    assert user2_response_data['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1


def test_num_dms_joined_after_leaving_dm(clear_data):
    # Register two users
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    user2_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Eugene', 'name_last': 'Gush'
    }).json()
    
    # Create a dm
    dm_data = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': [user2_data['auth_user_id']]
    }).json()
    
    # Leave the dm
    requests.post(BASE_URL + 'dm/leave/v1', json = {
        'token': user_data['token'],
        'dm_id': dm_data['dm_id']
    })
    
    # Call user/stats/v1
    response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    user2_response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user2_data['token']
    }).json()
    
    assert response_data['user_stats']['dms_joined'][-1]['num_dms_joined'] == 0 
    assert user2_response_data['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1 
    
def test_num_dms_joined_after_removing_dm(clear_data):
    # Register two users
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    user2_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Eugene', 'name_last': 'Gush'
    }).json()
    
    # Create a dm
    dm_data = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': [user2_data['auth_user_id']]
    }).json()
    
    # Call user/stats/v1
    user2_response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user2_data['token']
    }).json()
    
    assert user2_response_data['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1
    
    # Remove the dm
    requests.delete(BASE_URL + 'dm/remove/v1', json = {
        'token': user_data['token'], 'dm_id': dm_data['dm_id']
    })
    
    # Call user/stats/v1
    user1_response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    user2_response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user2_data['token']
    }).json()
        
    assert user1_response_data['user_stats']['dms_joined'][-1]['num_dms_joined'] == 0 
    assert user2_response_data['user_stats']['dms_joined'][-1]['num_dms_joined'] == 0

def test_correct_msgs_sent_after_standup(clear_data):
    # Register two users
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    user2_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Eugene', 'name_last': 'Gush'
    }).json()
    
    # Create a channel
    channel_data = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': True
    }).json()
    
    # Invite the other user to the channel
    requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user_data['token'],
        'channel_id': channel_data['channel_id'],
        'u_id': user2_data['auth_user_id']
    })
    
    # Start a standup
    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user_data['token'], 
        'channel_id': channel_data['channel_id'],
        'length': 2
    })
        
    # Send a message in the standup
    requests.post(BASE_URL + 'standup/send/v1', json = {
        'token': user_data['token'], 
        'channel_id': channel_data['channel_id'],
        'message': "hi"
    })
    
    time.sleep(2)
    
    # Call user stats
    user1_response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    user2_response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user2_data['token']
    }).json()
    
    assert user1_response_data['user_stats']['messages_sent'][-1]['num_messages_sent'] == 1
    assert user1_response_data['user_stats']['involvement_rate'] == 1
    
    assert user2_response_data['user_stats']['messages_sent'][-1]['num_messages_sent'] == 0

# for coverage    
def test_involvement_rate_greater_than_1(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # Create a channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_data['token'], 
        'name': 'channel', 
        'is_public': True
    }).json()
    
    # Create a dm
    dm_data = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_data['token'],
        'u_ids': []
    }).json()
    
    # Send multiple messages in the dm
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_data['token'],
        'dm_id': dm_data['dm_id'],
        'message': "hi"
    })
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_data['token'],
        'dm_id': dm_data['dm_id'],
        'message': "sup"
    })
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_data['token'],
        'dm_id': dm_data['dm_id'],
        'message': "another one"
    })
    
    # Remove the dm
    requests.delete(BASE_URL + 'dm/remove/v1', json = {
        'token': user_data['token'], 'dm_id': dm_data['dm_id']
    })
    
    # Call user stats
    user1_response_data = requests.get(BASE_URL + 'user/stats/v1', params = {
        'token': user_data['token']
    }).json()
    
    # Involvement rate should be (1 + 0 + 3)/(1 + 0 + 0) == 4
    # this should be capped at 1
    assert user1_response_data['user_stats']['involvement_rate'] == 1

