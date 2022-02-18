'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'users': [
        
    ],
    'channels': [
        
    ],
    'dms': [
    
    ],
    'stats': [
    
    ],
    'codes': [
    
    ]
}

'''
    'users': [
        {
            'u_id': 1,
            'email': "johnsmith@gmail.com",
            'password': "UNSW21",
            'name_first': "John",
            'name_last': "Smith",
            'handle_str': "johnsmith"
            'session_id': []
            'global_owner': True (if first user registered)
            'global_member': False (if first user registered)
            'profile_img_url': 'img_url'
            'user_stats': {
                               'channels_joined': [{num_channels_joined, time_stamp}],
                               'dms_joined': [{num_dms_joined, time_stamp}],
                               'messages_sent': [{num_messages_sent, time_stamp}],
                               'involvement_rate': 0
                          }
            'notifications': [
                                {
                                    'channel_id': 1, 
                                    'dm_id': -1, 
                                    'notification_message': "johnsmith added you to New Channel"
                                }
                             ]
        }
    ],
    'channels': [
        {
            'channel_id': 1,
            'name': "New Channel",
            'is_public': True,
            'owner_members': [users[0]],                        # [user, user, ...]
            'all_members': [users[0], users[1], users[2]],      # [user, user, ...], user[0] is explained below
            'messages': [
                            {
                                'message_id': 1,
                                'u_id': 1,
                                'message': "Hi",
                                'time_created': 1
                                'react': [{'react_id': 1, 'u_ids' : [], 'is_this_user_reacted': False}, ...]
                                'is_pinned': False
                            }
                        ]
            'standup':  {
                            'time_finish': 1,
                            'messages': []
                        }
        }
    ],
    'dms': [
        {
            'dm_id': 1,
            'name': "ahandle1, bhandle2, chandle3",
            'owner': users[0],
            'members': [users[0], users[1], users[2]],       # [user, user, ...]
            'messages': [
                            {
                                'message_id': 1,
                                'u_id': 1,
                                'message': "Hi",
                                'time_created': 1
                                'react': [{'react_id': 1, 'u_ids' : [], 'is_this_user_reacted': False}, ...]
                                'is_pinned': True
                            }
                        ]
        }
    ]
    
    'stats': [
        'workspace_stats': {
            'channels_exist': [{num_channels_exist, time_stamp}], 
            'dms_exist': [{num_dms_exist, time_stamp}], 
            'messages_exist': [{num_messages_exist, time_stamp}], 
            'utilization_rate': 0
        }
    ]

eg.
users[0] = {
                'u_id': 1,
                'email': "johnsmith@gmail.com",
                'password': "UNSW21",
                'name_first': "John",
                'name_last': "Smith",
                'handle_str': "placeholder"
           }
'''

## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

