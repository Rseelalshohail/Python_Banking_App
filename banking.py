import csv
import os

class Customer:
    def __init__(self, account_id, first_name, last_name, password, balance_checking, balance_savings):
        self.account_id = account_id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.balance_checking = float(balance_checking)  
        self.balance_savings = float(balance_savings)    


    def authenticate(self, password):
        return self.password == password

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
class Bank:
    def __init__(self, filename="bank.csv"):
        self.filename = filename
        self.customers = self.load_customers()

    def load_customers(self):
        """Load customers from bank.csv and store them as Customer objects."""
        customers = []
        with open(self.filename, mode='r', newline='') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                if len(row) == 6:
                    account_id, first_name, last_name, password, balance_checking, balance_savings = row
                    customers.append(Customer(account_id, first_name, last_name, password, float(balance_checking), float(balance_savings)))
        return customers


    def save_to_csv(self):
        with open(self.filename, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for customer in self.customers:
                writer.writerow([customer.account_id, customer.first_name, customer.last_name, customer.password, customer.balance_checking, customer.balance_savings])

    def add_customer(self, first_name, last_name, password):
        new_id = str(10000 + len(self.customers) + 1)
        new_customer = Customer(new_id, first_name, last_name, password, 0, 0)
        self.customers.append(new_customer)
        self.save_to_csv()
        print(f"✅ Account created successfully \nYour account ID is: {new_id} \nDon't forget to save it!")

    def get_customer_by_id(self, account_id):
        for customer in self.customers:
            if customer.account_id == account_id:
                return customer
        return None

    def login(self, account_id, password):
        customer = self.get_customer_by_id(account_id)
        if customer and customer.authenticate(password):
            return customer
        return None

class Account:
    def __init__(self, customer, bank):
        self.customer = customer
        self.bank = bank
        self.overdraft_count = 0  

    def deposit(self, amount, account_type):
        if amount <= 0:
            print("\n❌ Deposit amount must be greater than 0.")
            return
        new_balance = self.customer.get_balance(account_type) + amount
        self.customer.update_balance(account_type, new_balance)
        self.bank.save_to_csv()
        Transaction(self.customer.account_id, f"Deposit ({account_type})", amount, new_balance).log_transaction()
        print(f"\n✅ Deposit successful! New {account_type} balance: ${new_balance}")

    def withdraw(self, amount, account_type):
        balance = self.customer.get_balance(account_type)

        if amount > 100:
            print("\n❌ Withdrawal Denied: Cannot withdraw more than $100 at a time.")
            return

        if balance < 0 and amount > 100:
            print("\n❌ Withdrawal Denied: Cannot withdraw more than $100 while overdrawn.")
            return

        if balance - amount < -65:  
            print("\n❌ Withdrawal Denied: Account cannot go below -$100 after overdraft fee.")
            return

        if balance - amount < 0:
            print("\n⚠️ Overdraft! A $35 Fee Will Be Charged ⚠️")
            amount += 35  
            self.overdraft_count += 1  

        if self.overdraft_count >= 2:
            print("\n❌ Account Deactivated Due to Excessive Overdrafts.")
            return

        new_balance = balance - amount
        self.customer.update_balance(account_type, new_balance)
        self.bank.save_to_csv()
        Transaction(self.customer.account_id, f"Withdraw ({account_type})", amount, new_balance).log_transaction()
        print(f"\n✅ Withdrawal Successful! New {account_type} Balance: ${new_balance}")

    def transfer(self, amount, from_account, to_account, receiver_id=None):
        if amount <= 0:
            print("\n❌ Transfer amount must be greater than 0.")
            return

        