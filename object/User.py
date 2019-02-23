import json
from requests_oauthlib import OAuth1Session
import re
import settings
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import requests

class User:
    def __init__(self, user_name, password, email=None):
        self.user_name = user_name
        self.password= password
        self.email = email
        name_array = user_name.split('.')
        self.first_name =name_array[0]
        self.last_name ='.'.join(name_array[1:]) if len(name_array)>1 else ''

    @staticmethod
    def load(path):
        with open(path, encoding="utf-8") as file:
            file_content = file.read()
        json_object = json.loads(file_content)
        return json_object

    def oauth_login(self):
        session = OAuth1Session(
            settings.OAUTH_CONSUMER_KEY,
            client_secret=settings.OAUTH_CONSUMER_SECRET,
            callback_uri=settings.REDIRECT_URL +settings.OAUTH_AUTHORIZATION_PATH,
        )

        url = settings.API_HOST + settings.OAUTH_TOKEN_PATH
        response = session.fetch_request_token(url, verify=settings.VERIFY)

        self.oauth_token = response.get('oauth_token')
        self.oauth_secret = response.get('oauth_token_secret')

        url = settings.API_HOST + settings.OAUTH_AUTHORIZATION_PATH
        authorization_url = session.authorization_url(url)

        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(authorization_url)
        username_element = driver.find_element_by_name("username")
        username_element.send_keys(self.user_name)
        password_element = driver.find_element_by_name("password")
        password_element.send_keys(self.password)
        submit_button = driver.find_element_by_class_name("submit")
        submit_button.click()
        current_url = driver.current_url
        print(current_url)
        driver.close()
        p = re.compile(".*?oauth_token=(.*)&oauth_verifier=(.*)")
        result = p.search(current_url)
        try:
            self.oauth_verifier = result.group(2)
        except:
            print("login failed!!!")
            return None

        print("oauth_token: {}\noauth_secret: {}".format(self.oauth_token, self.oauth_secret))

        self.session = OAuth1Session(
            settings.OAUTH_CONSUMER_KEY,
            settings.OAUTH_CONSUMER_SECRET,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_secret,
            verifier=self.oauth_verifier
        )
        self.session.parse_authorization_response(authorization_url)
        url = settings.API_HOST + settings.OAUTH_ACCESS_TOKEN_PATH
        response = self.session.fetch_access_token(url)
        self.access_token = response.get('oauth_token')
        self.access_secret = response.get('oauth_token_secret')
        print("access_token: {}\naccess_secret: {}".format(self.access_token, self.access_secret))

        return self.session

    def direct_login(self):
        url = settings.API_HOST + settings.DIRECTLOGIN_PATH
        authorization = 'DirectLogin username="{}",password="{}",consumer_key="{}"'.format(  # noqa
            self.user_name,
            self.password,
            settings.OAUTH_CONSUMER_KEY)
        headers = {'Authorization': authorization}

        self.session = None
        try:
            response = requests.post(url, headers=headers)
            result = response.json()
            if response.status_code != 201:
                print("Login failed!!!")
            else:
                token = result['token']
                headers = {'Authorization': 'DirectLogin token={}'.format(token)}
                self.session = requests.Session()
                self.session.headers.update(headers)
        except requests.exceptions.ConnectionError as err:
            print("Login failed!!!")

        return self.session

    def get_user_private_account(self):

        result = self.session.get(settings.API_HOST+"/obp/v1.2.1/accounts/private")
        if result.status_code==200:
            return result.content
        else:
            return '{"accounts":[]}'

    def get_user_other_account(self, bank_id, account_id, view_id):

        result = self.session.get(
            settings.API_HOST+"/obp/v3.1.0/banks/"+bank_id+"/accounts/"+account_id+"/"+view_id+"/other_accounts")

        if result.status_code==200:
            return result.content
        else:
            return []

    def __str__(self):
        return self.user_name+"\t"+self.email

    def oauth_logout(self):
        pass

    def to_json(self):
        return {
            "email":self.email,
            "username":self.user_name,
            "password":self.password,
            "first_name":self.first_name,
            "last_name":self.last_name
        }

    def create_user(self, user):
        url = settings.API_HOST + "/obp/v2.0.0/users"
        result = self.session.request('POST', url, json=user.to_json(), verify=settings.VERIFY)
        if result.status_code == 201:
            print("saved {} as users".format(user.user_name))
            user_id = json.loads(result.text)['user_id']
            return True, user_id
        elif result.status_code == 409 and json.loads(result.text)['message']=='User with the same username already exists.':
            print("{} already exists".format(user.user_name))
            url = settings.API_HOST + "/obp/v3.0.0/users/username/{}".format(user.user_name)
            result = self.session.request('GET', url, verify=settings.VERIFY)
            user_id = json.loads(result.text)['user_id']
            return True, user_id
        else:
            print("did NOT save customer {}".format(
                result.content if result is not None and result.content is not None else ""))
            return False, None

    def addRole(self, user_id, role, bank_id=""):
        url = settings.API_HOST + "/obp/v2.0.0/users/{}/entitlements".format(user_id)
        entitlement = {
            "bank_id": bank_id,
            "role_name": role
        }
        result = self.session.request('POST', url, json=entitlement, verify=settings.VERIFY)
        if result.status_code == 201:
            print("add {} to {} {}".format(role, user_id, bank_id))
            return True
        else:
            print("did NOT save {} entitlement {}".format(role,
                result.content if result is not None and result.content is not None else ""))
            return False
