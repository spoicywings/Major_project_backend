import pytest
import requests
import json

from src import config
from src.error import InputError, AccessError

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
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw',
        'img_url': 'http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png',
        'x_start': 1, 'y_start': 1, 'x_end': 2, 'y_end': 2
    })
    
    assert response.status_code == AccessError.code
    
def test_http_status_not_200(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # img_url not found
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.jpg',
        'x_start': 1, 'y_start': 1, 'x_end': 2, 'y_end': 2
    })
    
    assert response.status_code == InputError.code
    
def test_x_start_not_within_dimensions_of_image(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # x_start not within dimensions of image (1020 x 510)
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://i.kym-cdn.com/photos/images/original/001/468/202/b02.jpg',
        'x_start': 1025, 'y_start': 10, 'x_end': 2000, 'y_end': 15
    })
    
    assert response.status_code == InputError.code

def test_y_start_not_within_dimensions_of_image(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # y_start not within dimensions of image (1020 x 510)
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://i.kym-cdn.com/photos/images/original/001/468/202/b02.jpg',
        'x_start': 10, 'y_start': 2000, 'x_end': 90, 'y_end': 2001
    })
    
    assert response.status_code == InputError.code

def test_x_end_not_within_dimensions_of_image(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # x_end not within dimensions of image (1020 x 510)
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://i.kym-cdn.com/photos/images/original/001/468/202/b02.jpg',
        'x_start': 10, 'y_start': 10, 'x_end': 1050, 'y_end': 15
    })
    
    assert response.status_code == InputError.code

def test_y_end_not_within_dimensions_of_image(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # y_end not within dimensions of image (1020 x 510)
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://i.kym-cdn.com/photos/images/original/001/468/202/b02.jpg',
        'x_start': 10, 'y_start': 10, 'x_end': 15, 'y_end': 2000
    })
    
    assert response.status_code == InputError.code
 
def test_x_end_less_than_x_start(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # x_end less than x_start
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://i.kym-cdn.com/photos/images/original/001/468/202/b02.jpg',
        'x_start': 10, 'y_start': 1, 'x_end': 5, 'y_end': 2
    })
    
    assert response.status_code == InputError.code

def test_y_end_less_than_y_start(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # y_end less than y_start
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://i.kym-cdn.com/photos/images/original/001/468/202/b02.jpg',
        'x_start': 1, 'y_start': 10, 'x_end': 2, 'y_end': 5
    })
    
    assert response.status_code == InputError.code
    
def test_image_not_jpg(clear_data):
    # Register one user
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    # img_url not jpg
    response = requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png',
        'x_start': 1, 'y_start': 1, 'x_end': 2, 'y_end': 2
    })
    
    assert response.status_code == InputError.code

def test_successful_uploadphoto(clear_data):
    # Register two users
    user_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user1@email.com', 'password': 'password',
        'name_first': 'Bill', 'name_last': 'Billy'
    }).json()
    
    u_id = user_data['auth_user_id']
    
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'user2@email.com', 'password': 'password',
        'name_first': 'Eugene', 'name_last': 'Gush'
    }).json()
    
    # Give valid img_url and dimensions
    requests.post(BASE_URL + 'user/profile/uploadphoto/v1', json = {
        'token': user_data['token'],
        'img_url': 'http://i.kym-cdn.com/photos/images/original/001/468/202/b02.jpg',
        'x_start': 0, 'y_start': 0, 'x_end': 100, 'y_end': 100
    })
    
    # Get user profile
    user_profile = requests.get(BASE_URL + 'user/profile/v1', params = {
        'token': user_data['token'], 'u_id': user_data['auth_user_id']
    }).json()
    
    assert user_profile['user']['profile_img_url'] == f'{BASE_URL}static/{u_id}.jpg'

    
