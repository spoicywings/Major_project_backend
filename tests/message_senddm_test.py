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
    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw',
        'dm_id': 1,
        'message': "hi"
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

    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': response_data['token'],
        'dm_id': 2,
        'message': "hi"
    })

    assert response.status_code == InputError.code

# Raise an InputError.code when message is less than 1 character
def test_less_than_1_message(clear_data):
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

    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': response_data['token'],
        'dm_id': 1,
        'message': ""
    })

    assert response.status_code == InputError.code

# Raise an InputError.code when message is more than 1000 character
def test_over_1000_message(clear_data):
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

    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': response_data['token'],
        'dm_id': 1,
        'message': "zvsXUlG9bFUiRIyYvqCS2TjxlNhZHtAbSddrfthNm62Uj5hRPXohUam2j4csgpfhuCsI2CNEYrCuFuS5OGvx2l7nvlGhRAXzx43OpCJnNWBf7BfGCeHom4ZKIcDyIbCMmdXkT8ESoiaROxHJvobqDDDIIoidWMbb0m2gInAb1WmczcZjYTENcsLsmZboSClWFgUzM5yC7HdXbkjSyLU8gVcS93NiJ4Zeeg9vooOOmZlSfqBMd7YgAeJJSP2WYvteZdEVP89zUX86UALO1Vyok0hHuV7eTKSf1Lkj8UxR3uIcVXeYR2xgM6B0h95dUCj171SSSyEwiWwRz2zVl7VLbYNdJXdaWmjmhTmCkPLFxc3ZY2R1udz49jgsOZIxUgTPCGpUBvQEe5yD1UYgQcaCmxpkHsKRuvCDyHpq6Fjx2PPq0O9n0Ye6ZjDfVWWW62IIyOuvYUJD9iyj1jzpincbPl9oaKKMj8scV0WfzEcfENZkqoTFRwUolefneHhVQIQ6r6vSYvHBhAB96YPloebjbaZSPyNpqbPB2YG2M5Kfw1Eg8Ew47fhvFAvYMyS17aYCmZt70XJFcKfGEsNmrpdKrhaN04KYaXvFcaoN8PbvjtCiCC51nUkquGNsDXazAqXQeKOVKKMNJr9m3l25ODihflt5ln7QSwMOdjujCP1xXwsk8Q0hYZTVcKTeub42U2rKN8YKaK6kpSA3ZIxsu2YtTCqGfs5OW0Ikvf0oZhvaTAs0avpF8iJoeBHDfiaHBdDkq3A2xalCzW1wu0j2wfupi5kPmt2SzziY1MNI00Nhm1DG4fvmLwLegabePlX4pxJNhzNKTAQjlQVF2wHMTjXZmnTunpuCY5pGFNcjo7g2OTKjw8mfrWOWVq2i8VQ7h3o73GTD7odn4oNStkCVC8Do4TIvFSilvPK83HsC7aPArtVJHUC4W0pBq6LMYC0bAe2CkfUdid7tgGHqwKZwfgtFn1GFCigysuzgvwuWfGj1D"
    })

    assert response.status_code == InputError.code

# Raises an AccessError.code when valid user is not member of DM
def test_not_member(clear_data, dm_create_single):
    data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })
    
    not_member = data.json()
    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': not_member['token'],
        'dm_id': 1,
        'message': "hi"
    })

    assert response.status_code == AccessError.code

# Test that the function sends a message and generates an id
def test_valid_dm_message(clear_data):
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

    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': response_data['token'],
        'dm_id': 1,
        'message': "hi"
    })
    
    response_data = response.json()
    
    assert response_data['message_id'] == 1

# Case where message_id are unique even when they are in different DMs 
def test_message_id_different(clear_data):
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

    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': response_data['token'],
        'dm_id': 1,
        'message': "hi"
    })
    

    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jaskon'
    })
    
    response_data = response.json()
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': response_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': response_data['token'],
        'dm_id': 2,
        'message': "hi"
    })
    
    response_data = response.json()
    
    assert response_data['message_id'] == 2

# Message_ids are unique even when they are in the same DM
def test_messages_in_same_dm(clear_data):
    member = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    member_data = member.json()
    
    owner = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    owner_data = owner.json()
    
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': owner_data['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': owner_data['token'],
        'dm_id': 1,
        'message': "hi"
    })

    response = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': member_data['token'],
        'dm_id': 1,
        'message': "hey"
    })
    
    response_data = response.json()
    
    assert response_data['message_id'] == 2
