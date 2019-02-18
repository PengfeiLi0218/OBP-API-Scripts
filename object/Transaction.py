import json

class Transaction:
    def __init__(self, id, this_account, counterparty, detail):
        self.id = id
        self.this_account_id = this_account['id']
        self.this_account_bank = this_account['bank']
        self.counterparty = counterparty['name']
        self.detail_type= detail['type']
        self.detail_description= detail['description']
        self.detail_posted= detail['posted']
        self.detail_completed= detail['completed']
        self.detail_new_balance= detail['new_balance']
        self.detail_value= detail['value']

    @staticmethod
    def load(path):
        with open(path, encoding="utf-8") as file:
            file_content = file.read()
        json_object = json.loads(file_content)
        return json_object

