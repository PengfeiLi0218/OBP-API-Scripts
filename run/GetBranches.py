import settings
from object.Branch import Branch
import os
import json

from object.User import User

if __name__=='__main__':
    if not os.path.exists("data.json"):
        json_string, json_atm = Branch.get_branches_from_web("https://www.hsbc.com.hk/personal/contact-us/branch-locator.html")

        with open('data.json', 'w') as outfile:
            outfile.write(json_string)

        with open('atm.json', 'w') as outfile:
            outfile.write(json_atm)

    with open('data.json') as f:
        data = json.load(f)
    with open('atm.json') as f:
        data_atms = json.load(f)
    adminUserUsername = settings.ADMIN_USERNAME
    adminPassword = settings.ADMIN_PASSWORD

    print("login as administrator: ")
    admin_user = User(adminUserUsername, adminPassword)

    session = admin_user.direct_login()
    print("ok!!!")
    url = settings.API_HOST + "/obp/v3.1.0/banks/{}/branches".format("hsbc.01.hk.hsbc")
    url_atm = settings.API_HOST + "/obp/v3.1.0/banks/{}/atms".format("hsbc.01.hk.hsbc")
    for row in data:
        result = session.request('POST', url, json=row, verify=settings.VERIFY)
        if result.status_code == 201:
            print("saved {} as branch".format(row['name']))

        else:
            print("did NOT save branch {}, \nmessage: {}".format(row['name'], result.text))
    for row in data_atms:
        result = session.request('POST', url_atm, json=row, verify=settings.VERIFY)
        if result.status_code == 201:
            print("saved {} as atms".format(row['name']))

        else:
            print("did NOT save atm {}, \nmessage: {}".format(row['name'], result.text))