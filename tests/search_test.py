import pytest
import requests
import json

from src import config
from src.error import InputError, AccessError

BASE_URL = config.url

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

@pytest.fixture
def dm_create_single():
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })

@pytest.fixture
def channel_create_single():
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

# Raises an AccessError when token is invalid
def test_invalid_token(clear_data, channel_create_single, dm_create_single):
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 
        'query_str': 'hi'
    })
    
    assert response.status_code == AccessError.code

# Raises an InputError when query_str less than 1
def test_no_query_str(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })

    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user2_data['token'], 
        'query_str': ''
    })
    
    assert response.status_code == InputError.code

# Raises an InputError when query_str over 1000
def test_large_query_str(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })

    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user2_data['token'], 
        'query_str': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nd'
    })
    
    assert response.status_code == InputError.code

# Raises an AccessError when query_str and token are invalid
def test_invalid_both(clear_data, dm_create_single):
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 
        'query_str': ''
    })
    
    assert response.status_code == AccessError.code

# When user has messages in both dm and channel
def test_message_in_both_dm_channel(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jefflee@gmail.com', 'password': 'password', 
        'name_first': 'Jeff', 'name_last': 'Lee'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user2_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user2_data['token'],
        'channel_id': 1,
        'message': "hey"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user2_data['token'],
        'dm_id': 1,
        'message': "hey m8"
    })
    
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user2_data['token'], 
        'query_str': "hey"
    })
    
    response_data = response.json()
    
    assert response_data['messages'][0]['message'] == "hey"
    assert response_data['messages'][1]['message'] == "hey m8"

# When user has messages in both dm and channel but leaves dm
def test_message_in_both_dm_channel_user_leaves_dm(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jefflee@gmail.com', 'password': 'password', 
        'name_first': 'Jeff', 'name_last': 'Lee'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user2_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user2_data['token'],
        'channel_id': 1,
        'message': "hey"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user2_data['token'],
        'dm_id': 1,
        'message': "hey m8"
    })
    
    requests.post(BASE_URL + 'dm/leave/v1', json = {
        'token': user2_data['token'],
        'dm_id': 1
    })
    
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user2_data['token'], 
        'query_str': "hey"
    })
    
    response_data = response.json()
    
    assert response_data['messages'][0]['message'] == "hey"
    assert len(response_data['messages']) == 1

# When user has messages in both dm and channel but leaves channel
def test_message_in_both_dm_channel_user_leaves_channel(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jefflee@gmail.com', 'password': 'password', 
        'name_first': 'Jeff', 'name_last': 'Lee'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user2_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user2_data['token'],
        'channel_id': 1,
        'message': "hey"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user2_data['token'],
        'dm_id': 1,
        'message': "hey m8"
    })
    
    requests.post(BASE_URL + 'channel/leave/v1', json = {
        'token': user2_data['token'],
        'channel_id': 1
    })
    
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user2_data['token'], 
        'query_str': "hey"
    })
    
    response_data = response.json()
    
    assert response_data['messages'][0]['message'] == "hey m8"
    assert len(response_data['messages']) == 1

# When user has multiple messages in dm
def test_multiple_messages_in_dm(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jefflee@gmail.com', 'password': 'password', 
        'name_first': 'Jeff', 'name_last': 'Lee'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user2_data['token'],
        'dm_id': 1,
        'message': "hey m8"
    })
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user2_data['token'],
        'dm_id': 1,
        'message': "bye"
    })
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user2_data['token'],
        'dm_id': 1,
        'message': "heyasjdnsandsads"
    })
    
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user2_data['token'], 
        'query_str': "hey"
    })
    
    response_data = response.json()
    
    assert response_data['messages'][0]['message'] == "hey m8"
    assert response_data['messages'][1]['message'] == "heyasjdnsandsads"

# When user has multiple messages in channel
def test_multiple_messages_in_channel(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jefflee@gmail.com', 'password': 'password', 
        'name_first': 'Jeff', 'name_last': 'Lee'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_data['token'],
        'channel_id': 1,
        'message': "hey m8"
    })
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_data['token'],
        'channel_id': 1,
        'message': "bye"
    })
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_data['token'],
        'channel_id': 1,
        'message': "heyasjdnsandsads"
    })
    
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user1_data['token'], 
        'query_str': "hey"
    })
    
    response_data = response.json()
    
    assert response_data['messages'][0]['message'] == "hey m8"
    assert response_data['messages'][1]['message'] == "heyasjdnsandsads"
    
# When query has no matches
def test_no_matches(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jefflee@gmail.com', 'password': 'password', 
        'name_first': 'Jeff', 'name_last': 'Lee'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user2_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user2_data['token'],
        'dm_id': 1,
        'message': "hey m8"
    })
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user2_data['token'],
        'channel_id': 1,
        'message': "heyasjdnsandsads"
    })
    
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user2_data['token'], 
        'query_str': "bye"
    })
    
    response_data = response.json()
    
    assert response_data['messages'] == []
    
# When query has no matches as there are no messages
def test_user_not_in_channel_dm(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jefflee@gmail.com', 'password': 'password', 
        'name_first': 'Jeff', 'name_last': 'Lee'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user2_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user2_data['token'],
        'u_ids': [user1_data['auth_user_id']]
    })
    
    response = requests.get(BASE_URL + 'search/v1', params = {
        'token': user1_data['token'], 
        'query_str': "hi"
    })
    
    response_data = response.json()
    
    assert response_data['messages'] == []
