import sys
import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config

import threading
from src.data_store import data_store
import json

from src.channel import channel_join_v1, channel_leave_v1, channel_addowner_v1, channel_details_v1, channel_invite_v1, channel_messages_v1
from src.messages import message_send_v1, message_edit_v1, message_remove_v1, message_sendlater_v1, message_sendlaterdm_v1, message_share_v1
from src.channel import channel_removeowner_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.other import clear_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
from src.user_profile import user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1
from src.user_profile import user_profile_uploadphoto_v1
from src.users_all import users_all_v1
from src.message import message_senddm_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src.admin import admin_userpermission_change_v1, admin_user_remove_v1
from src.stats import user_stats_v1, users_stats_v1
from src.search import search_v1
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
from src.notifications import notifications_get_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

with open('data_store.json', 'r') as FILE:
    datastore = json.load(FILE)
    data_store.set(datastore)

def save():
    store = data_store.get()
    threading.Timer(1.0, save).start()
    with open('data_store.json', 'w') as FILE:
        json.dump(store, FILE)

save()

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

# CLEAR
@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({
    })    

# AUTH
@APP.route("/auth/register/v2", methods=['POST']) 
def register():
    data = request.get_json()
    register_return = auth_register_v1(data['email'], data['password'], data['name_first'], data['name_last'])
    return dumps({
        'auth_user_id': register_return['auth_user_id'],
        'token': register_return['token']
    })
   
@APP.route("/auth/login/v2", methods=['POST'])
def login():
    data = request.get_json()
    login_return = auth_login_v1(data['email'], data['password'])
    return dumps({
        'auth_user_id': login_return['auth_user_id'],
        'token': login_return['token']
    })
    
@APP.route("/auth/logout/v1", methods=['POST'])
def logout():
    data = request.get_json()
    auth_logout_v1(data['token'])
    
    return dumps({
    })
    
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def reset_request():
    data = request.get_json()
    auth_passwordreset_request_v1(data['email'])
    return dumps({
    })   

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def reset():
    data = request.get_json()
    auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])
    return dumps({
    })   

# CHANNELS 
@APP.route("/channels/create/v2", methods=['POST'])
def create():
    data = request.get_json()
    create_return = channels_create_v1(data['token'], data['name'], data['is_public'])
    return dumps({
        'channel_id': create_return['channel_id']
    })       

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    user_token = request.args.get('token')
    details = channels_list_v1(user_token)
    return dumps(details)

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    user_token = request.args.get('token')
    details = channels_listall_v1(user_token)
    return dumps(details)

# DMS
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    request_data = request.get_json()
    dm_create_return = dm_create_v1(request_data['token'], request_data['u_ids'])
    return dumps({
        'dm_id': dm_create_return['dm_id']
    })

@APP.route("/dm/list/v1", methods=['GET'])   
def dm_list():
    token = request.args.get('token')
    dm_list_return = dm_list_v1(token)
    
    return dumps({
        'dms': dm_list_return['dms']
    })
    
@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    request_data = request.get_json()

    dm_remove_v1(request_data['token'], request_data['dm_id'])
    
    return dumps({
    })
    
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    dm_details_return = dm_details_v1(token, dm_id)
    
    return dumps({
        'name': dm_details_return['name'],
        'members': dm_details_return['members']
    })
    
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    request_data = request.get_json()
    dm_leave_v1(request_data['token'], request_data['dm_id'])
    
    return dumps({
    })

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))

    dm_messages_return = dm_messages_v1(token, dm_id, start)
    
    return dumps({
        'messages': dm_messages_return['messages'],
        'start': dm_messages_return['start'],
        'end': dm_messages_return['end']
    })

# MESSAGE
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    request_data = request.get_json()
    message_senddm_return = message_senddm_v1(request_data['token'], request_data['dm_id'], request_data['message'])
    
    return dumps({
        'message_id': message_senddm_return['message_id']
    })

@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    data = request.get_json()
    message_react_v1(data['token'], data['message_id'], data['react_id'])
    return dumps({})

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    data = request.get_json()
    message_unreact_v1(data['token'], data['message_id'], data['react_id'])
    return dumps({})

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    data = request.get_json()
    message_pin_v1(data['token'], data['message_id'])
    return dumps({})

@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    data = request.get_json()
    message_unpin_v1(data['token'], data['message_id'])
    return dumps({})
    
# CHANNEL
@APP.route("/channel/join/v2", methods=['POST'])
def join():
    data = request.get_json()
    channel_join_v1(data['token'], data['channel_id'])
    return dumps({        
    }) 
    
@APP.route("/channel/leave/v1", methods=['POST'])
def leave():
    data = request.get_json()
    channel_leave_v1(data['token'], data['channel_id'])
    return dumps({        
    })        
 

@APP.route("/channel/details/v2", methods=["GET"])
def get_channel_details():
    user_token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    details = channel_details_v1(user_token, int(channel_id))
    return dumps(details)
    
@APP.route("/channel/addowner/v1", methods=['POST'])
def addowner():
    data = request.get_json()
    channel_addowner_v1(data['token'], data['channel_id'], data['u_id'])
    return dumps({        
    }) 

@APP.route("/channel/removeowner/v1", methods=['POST'])
def removeowner():
    data = request.get_json()
    channel_removeowner_v1(data['token'], data['channel_id'], data['u_id'])
    return dumps({        
    })            

    
# USER PROFILE
@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    user_return = user_profile_v1(token, u_id)
    
    return dumps({
        'user': user_return
    })
    
@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname():
    data = request.get_json()
    user_profile_setname_v1(data['token'], data['name_first'], data['name_last'])
    
    return dumps({
    })
    
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail():
    data = request.get_json()
    user_profile_setemail_v1(data['token'], data['email'])

    return dumps({
    })
    
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    data = request.get_json()
    user_profile_sethandle_v1(data['token'], data['handle_str'])   
    
    return dumps({
    })
    
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto():
    data = request.get_json()
    user_profile_uploadphoto_v1(data['token'], data['img_url'], data['x_start'], data['y_start'], data['x_end'], data['y_end'])
    
    return dumps({
    })

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)

# USERS
@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    token = request.args.get('token')
    user_return = users_all_v1(token)['users']
    
    return dumps({
        'users': user_return
    })

# ADMIN
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def change_permission():
    data = request.get_json()
    admin_userpermission_change_v1(data['token'], data['u_id'], data['permission_id'])
    return dumps({})

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_remove_user():
    request_data = request.get_json()

    admin_user_remove_v1(request_data['token'], request_data['u_id'])
    return dumps({})

@APP.route("/channel/invite/v2", methods=['POST'])
def invite():
    data = request.get_json()
    channel_invite_v1(data['token'], data['channel_id'], data['u_id'])
    return dumps({})

@APP.route('/channel/messages/v2', methods=['GET'])
def messages():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    messages_return = channel_messages_v1(token, int(channel_id), int(start))
    return dumps({
        'messages': messages_return['messages'],
        'start': messages_return['start'],
        'end': messages_return['end']
    })
    
# MESSAGES
@APP.route('/message/send/v1', methods=['POST'])
def message_send():
    data = request.get_json()
    message_id = message_send_v1(data['token'], data['channel_id'], data['message'])
    return dumps({
        'message_id': message_id['message_id']
        })

@APP.route('/message/edit/v1', methods=['PUT'])
def message_edit():
    data = request.get_json()
    message_edit_v1(data['token'], data['message_id'], data['message'])
    return dumps({})

@APP.route('/message/remove/v1', methods=['DELETE'])
def message_remove():
    data = request.get_json()
    message_remove_v1(data['token'], data['message_id'])
    return dumps({})

@APP.route('/message/sendlater/v1', methods=['POST'])
def message_sendlater():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    message = data['message']
    time_sent = data['time_sent']
    message_id = message_sendlater_v1(token, int(channel_id), message, time_sent)
    return dumps(message_id)

@APP.route('/message/sendlaterdm/v1', methods=['POST'])
def message_sendlater_dm():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    message = data['message']
    time_sent = data['time_sent']
    message_id = message_sendlaterdm_v1(token, int(dm_id), message, time_sent)
    return dumps(message_id)

@APP.route('/message/share/v1', methods=['POST'])
def message_share():
    data = request.get_json()
    token = data['token']
    og_message_id = data['og_message_id']
    message = data['message']
    channel_id = data['channel_id']
    dm_id = data['dm_id']
    message_id = message_share_v1(token, int(og_message_id), message, int(channel_id), int(dm_id))
    return dumps(message_id)
    
# STATS
@APP.route('/user/stats/v1', methods=['GET'])
def user_stats():
    token = request.args.get('token')
    user_stats = user_stats_v1(token)['user_stats']
    
    return dumps({
        'user_stats': user_stats
    })
    
@APP.route('/users/stats/v1', methods=['GET'])
def users_stats():
    token = request.args.get('token')
    workspace_stats = users_stats_v1(token)['workspace_stats']
    
    return dumps({
        'workspace_stats': workspace_stats
    })

# SEARCH
@APP.route("/search/v1", methods=['GET'])
def search():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    
    search_return = search_v1(token, query_str)
    
    return dumps({
        'messages': search_return['messages']
    })

# STANDUP
@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    
    standup_start_return = standup_start_v1(data['token'], data['channel_id'], data['length'])
    
    return dumps({
        'time_finish': standup_start_return['time_finish']
    })

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    
    standup_active_return = standup_active_v1(token, channel_id)
    
    return dumps({
        'is_active': standup_active_return['is_active'],
        'time_finish': standup_active_return['time_finish']
    })

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    data = request.get_json()
    
    standup_send_v1(data['token'], data['channel_id'], data['message'])
    
    return dumps({
    })

# NOTIFICATIONS
@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get():
    token = request.args.get('token')
    
    notifications_get_return = notifications_get_v1(token)
    
    return dumps({
        'notifications': notifications_get_return['notifications']
    })

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
