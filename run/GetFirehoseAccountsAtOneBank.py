import settings
from object.User import User
import json

if __name__=='__main__':
    adminUserUsername = settings.ADMIN_USERNAME
    adminPassword = settings.ADMIN_PASSWORD

    print("login as user: ")
    admin_user = User(adminUserUsername, adminPassword)
    session = admin_user.direct_login()
    print("ok!!!")

    url = settings.API_HOST + '/obp/v3.0.0/banks'
    result = session.request('GET', url, verify=settings.VERIFY)
    banks = [bank['id'] for bank in json.loads(result.content)['banks']]

    for bank in banks:
        url = settings.API_HOST + '/obp/v3.0.0/banks/{}/firehose/accounts/views/{}'.format(bank, "owner")
        result = session.request('GET', url, verify=settings.VERIFY)
        if result.status_code==200:
            accounts_list = json.loads(result.content)['accounts']
            for account in accounts_list:
                print(json.dumps(account, indent=4))
                firehose_url = settings.API_HOST + '/obp/v3.0.0/banks/{}/firehose/accounts/{}/views/{}/transactions'\
                    .format(bank,account['id'], "owner")
                firehose_result= session.request('GET', url, verify=settings.VERIFY)
                print("firehose transactions:")
                if firehose_result.status_code==200:
                    print(firehose_result.content)
                else:
                    print("{} get failed".format(account['id']))

                transaction_url = settings.API_HOST + '/obp/v3.0.0/banks/{}/accounts/{}/{}/transactions'\
                    .format(bank,account['id'], "owner")
                transaction_result = session.request('GET', url, verify=settings.VERIFY)
                print("transactions:")
                if transaction_result.status_code==200:
                    print(transaction_result.content)
                else:
                    print("{} get failed".format(account['id']))