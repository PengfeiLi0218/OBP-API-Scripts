import settings

import json
from object.User import User

exclude_roles = [
    'CanCreateEntitlementAtAnyBank',
    'CanCreateEntitlementAtOneBank',
    'CanDeleteEntitlementAtAnyBank',
    'CanDeleteEntitlementAtOneBank',
    'CanDeleteEntitlementRequestsAtAnyBank',
    'CanDeleteEntitlementRequestsAtOneBank',
    'CanDeleteScopeAtAnyBank',
    'CanDisableConsumers',
    'CanEnableConsumers',
    'CanCreateSandbox',
    'CanGetAnyUser',
    'CanGetConsumers'
]

def is_available(role):
    if role in exclude_roles:
        return False
    elif 'scope' in role.lower():
        return False
    elif 'entitlement' in role.lower():
        return False
    else:
        return True

if __name__=="__main__":

    adminUserUsername = settings.ADMIN_USERNAME
    adminPassword = settings.ADMIN_PASSWORD

    print("login as administrator: ")
    admin_user = User(adminUserUsername, adminPassword)
    session = admin_user.direct_login()
    print("ok!!!")

    json_object_user = User.load(settings.FILE_ROOT + "users.json")
    url = settings.API_HOST + '/obp/v3.0.0/banks'
    result = session.request('GET', url, verify=settings.VERIFY)
    banks = [bank['id'] for bank in json.loads(result.content)['banks']]

    url = settings.API_HOST + '/obp/v3.1.0/roles'
    result = session.request('GET', url, verify=settings.VERIFY)
    roles = json.loads(result.content)['roles']


    if 'users' in json_object_user:
        users = json_object_user['users']
        for user in users:
            user_name = user['user_name']
            password = user['password']
            email = user['email']

            user_object = User(user_name, password, email)
            flag, user_id = admin_user.create_user(user_object)
            if flag:
                for role in roles:
                    if not is_available(role['role']):
                        print('{} skip!!!'.format(role['role']))
                        continue
                    if role['requires_bank_id']:
                        for bank_id in banks:
                            admin_user.addRole(user_id, role['role'], bank_id)
                    else:
                        admin_user.addRole(user_id, role['role'])