import settings

import json
from object.User import User

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
    if 'users' in json_object_user:
        users = json_object_user['users']
        for user in users:
            user_name = user['user_name']
            password = user['password']
            email = user['email']

            user_object = User(user_name, password, email)
            flag, user_id = admin_user.create_user(user_object)
            if flag:
                admin_user.addRole(user_id, "CanUseFirehoseAtAnyBank")
                admin_user.addRole(user_id, "CanCreateBank")
                admin_user.addRole(user_id, "CanCreateAtmAtAnyBank")
                for bank_id in banks:
                    admin_user.addRole(user_id, "CanCreateAccount", bank_id)
                    admin_user.addRole(user_id, "CanCreateBranch", bank_id)
