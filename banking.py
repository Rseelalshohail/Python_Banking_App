import csv
import os

class Customer():
    def __init__(self, account_id, first_name, last_name, password, balance_checking, balance_savings):
        self.account_id = account_id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.balance_checking = balance_checking
        self.balance_savings = balance_savings

    def authenticate(self, password):
        return self.password == password #???

    def get_balance(self, account_type):
        if account_type == "checking":
            return self.balance_checking
        elif account_type == "savings":
            return self.balance_savings
        else:
            raise ValueError("Invalid account type")

    def update_balance(self, account_type, new_amount):
        if account_type == "checking":
            self.balance_checking = new_amount
        elif account_type == "savings":
            self.balance_savings = new_amount
        else:
            raise ValueError("Invalid account type")    

class Bank():
    pass

class Account():
    pass

class Transaction():
    pass

