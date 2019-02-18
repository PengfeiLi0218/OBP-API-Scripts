import settings
from object.Transaction import Transaction

if __name__=='__main__':
    json_transaction = Transaction.load(settings.FILE_ROOT+"transactions.json")

    if 'transactions' in json_transaction:
        transactions = json_transaction['transactions']
        for transaction in transactions:
            transaction_object = Transaction(transaction['id'], transaction['this_account'], transaction['counterparty'], transaction['details'])
            print(transaction_object.detail_value)