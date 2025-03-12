import csv
import os
import datetime

OVERDRAFT_LIMIT = -100
OVERDRAFT_FEE = 35
MAX_WITHDRAWAL = 100

class Customer:
    def __init__(self, account_id, first_name, last_name, password):
        self.account_id = account_id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.balance_checking = None
        self.balance_savings = None

    def authenticate(self, password):
        return self.password == password

    def get_balance(self, account_type):
        if account_type == "checking" and self.balance_checking is not None:
            return self.balance_checking
        elif account_type == "savings" and self.balance_savings is not None:
            return self.balance_savings
        raise ValueError("Account not created. Please create the account first.")

    def update_balance(self, account_type, new_amount):
        if account_type == "checking" and self.balance_checking is not None:
            self.balance_checking = new_amount
        elif account_type == "savings" and self.balance_savings is not None:
            self.balance_savings = new_amount
        else:
            raise ValueError("Account not created. Please create the account first.")

    def create_account(self, account_type):
        if account_type == "checking" and self.balance_checking is None:
            self.balance_checking = 0.0
        elif account_type == "savings" and self.balance_savings is None:
            self.balance_savings = 0.0
        else:
            raise ValueError("Account already exists")

class Bank:
    def __init__(self, filename="bank.csv"):
        self.filename = filename
        self.customers = self.load_customers()

    def load_customers(self):
        customers = []
        if os.path.exists(self.filename):
            with open(self.filename, mode='r', newline='') as file:
                reader = csv.reader(file, delimiter=';')
                next(reader)  
                for row in reader:
                    if len(row) == 6:
                        account_id, first_name, last_name, password, balance_checking, balance_savings = row
                        customer = Customer(account_id, first_name, last_name, password)
                        customer.balance_checking = float(balance_checking) if balance_checking else None
                        customer.balance_savings = float(balance_savings) if balance_savings else None
                        customers.append(customer)
        return customers


    def save_to_csv(self):
        with open(self.filename, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["Account ID", "First Name", "Last Name", "Password", "Checking Balance", "Savings Balance"])
            for customer in self.customers:
                writer.writerow([
                    customer.account_id,
                    customer.first_name,
                    customer.last_name,
                    customer.password,
                    customer.balance_checking or "",
                    customer.balance_savings or ""
                ])

    def add_customer(self, first_name, last_name, password):
        new_id = str(10000 + len(self.customers) + 1)
        new_customer = Customer(new_id, first_name, last_name, password)
        self.customers.append(new_customer)
        self.save_to_csv()
        print(f"\n✅ Account created successfully!\nYour account ID is: {new_id}")

    def get_customer_by_id(self, account_id):
        return next((c for c in self.customers if c.account_id == account_id), None)

    def login(self, account_id, password):
        customer = self.get_customer_by_id(account_id)
        return customer if customer and customer.authenticate(password) else None

class Account:
    def __init__(self, customer, bank):
        self.customer = customer
        self.bank = bank
        self.overdraft_count = 0
        self.account_deactivated = False

    def deposit(self, amount, account_type):
        if amount <= 0:
            print("\n❌ Deposit must be greater than 0.")
            return

        try:
            new_balance = self.customer.get_balance(account_type) + amount
            self.customer.update_balance(account_type, new_balance)
            self.bank.save_to_csv()
            Transaction(self.customer.account_id, f"Deposit ({account_type})", amount, new_balance).log_transaction()
            print(f"\n✅ Deposit successful! New {account_type} balance: ${new_balance:.2f}")

            if self.account_deactivated and new_balance >= 0:
                self.account_deactivated = False
                self.overdraft_count = 0
                print("\n✅ Account reactivated.")
        except ValueError as e:
            print(f"\n❌ {e}")

    def withdraw(self, amount, account_type):
        if amount <= 0:
            print("\n❌ Withdrawal must be greater than 0.")
            return
        if self.account_deactivated:
            print("\n❌ Withdrawal denied. Account is deactivated.")
            return

        try:
            balance = self.customer.get_balance(account_type)

            if amount > MAX_WITHDRAWAL:
                print("\n❌ Cannot withdraw more than $100 at a time.")
                return

            if balance - amount < OVERDRAFT_LIMIT + OVERDRAFT_FEE:
                print("\n❌ Withdrawal denied. Exceeds overdraft limit.")
                return

            if balance - amount < 0:
                print("\n⚠️ Overdraft alert! $35 fee applied.")
                amount += OVERDRAFT_FEE
                self.overdraft_count += 1

            if self.overdraft_count > 2:
                self.account_deactivated = True
                print("\n❌ Account deactivated due to repeated overdrafts.")
                return

            new_balance = balance - amount
            self.customer.update_balance(account_type, new_balance)
            self.bank.save_to_csv()
            Transaction(self.customer.account_id, f"Withdraw ({account_type})", amount, new_balance).log_transaction()
            print(f"\n✅ Withdrawal successful. New {account_type} balance: ${new_balance:.2f}")
        except ValueError as e:
            print(f"\n❌ {e}")

    def transfer(self, amount, from_account, to_account, receiver_id=None):
        if amount <= 0:
            print("\n❌ Transfer must be greater than 0.")
            return
        if self.account_deactivated:
            print("\n❌ Transfer denied. Account is deactivated.")
            return

        try:
            if receiver_id:
                receiver = self.bank.get_customer_by_id(receiver_id)
                if not receiver:
                    print("\n❌ Receiver account not found.")
                    return
                if self.customer.get_balance(from_account) < amount:
                    print("\n❌ Insufficient funds for transfer.")
                    return

                self.customer.update_balance(from_account, self.customer.get_balance(from_account) - amount)
                receiver.update_balance(to_account, receiver.get_balance(to_account) + amount)
                self.bank.save_to_csv()
                Transaction(self.customer.account_id, f"Transfer to {receiver_id}", amount, receiver.get_balance(to_account)).log_transaction()
                print(f"\n✅ Transfer successful. ${amount:.2f} sent to {receiver.first_name} {receiver.last_name}.")
            else:
                if self.customer.get_balance(from_account) < amount:
                    print("\n❌ Insufficient funds for internal transfer.")
                    return
                self.customer.update_balance(from_account, self.customer.get_balance(from_account) - amount)
                self.customer.update_balance(to_account, self.customer.get_balance(to_account) + amount)
                self.bank.save_to_csv()
                Transaction(self.customer.account_id, f"Internal Transfer ({from_account} to {to_account})", amount, self.customer.get_balance(to_account)).log_transaction()
                print(f"\n✅ Transfer successful. New {to_account} balance: ${self.customer.get_balance(to_account):.2f}")
        except ValueError as e:
            print(f"\n❌ {e}")

class Transaction:
    def __init__(self, customer_id, transaction_type, amount, resulting_balance):
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.customer_id = customer_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.resulting_balance = resulting_balance

    def log_transaction(self):
        with open("transactions.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                self.date,
                self.customer_id,
                self.transaction_type,
                self.amount,
                self.resulting_balance
            ])

def main():
    bank = Bank()
    print("\n💰 Welcome to ACME Bank!")
    
    while True:
        print("\n-------------------------------")
        print("1. Create a New Account")
        print("2. Sign In")
        print("3. Exit")
        print("-------------------------------")
        choice = input("Choose an option: ")

        if choice == "1":
            first_name = input("\nEnter First Name: ")
            last_name = input("Enter Last Name: ")
            password = input("Create a Password: ")
            bank.add_customer(first_name, last_name, password)

        elif choice == "2":
            account_id = input("\nEnter Your Account ID: ")
            password = input("Enter Your Password: ")
            customer = bank.login(account_id, password)
            if customer:
                print(f"\n✅ Login Successful! Welcome, {customer.first_name}.")
                account = Account(customer, bank)
                user_menu(account)
            else:
                print("\n❌ Invalid Credentials. Try Again.")

        elif choice == "3":
            print("\nThank You for Banking with ACME! Goodbye.")
            break
        else:
            print("\n❌ Invalid Choice. Please Try Again.")

def user_menu(account):
    while True:
        print("\n-------------------------------------")
        print("🏦  BANKING MENU")
        print("-------------------------------------")
        print("1. View Account Balances")
        print("2. Withdraw Money")
        print("3. Deposit Money")
        print("4. Transfer Money")
        print("5. Create Savings / Checking Account")
        print("6. Logout")
        print("-------------------------------------")
        choice = input("Choose an option: ")

        if choice == "1":
            print("\n💰 Account Balances")
            try:
                print(f"   - Savings Balance: ${account.customer.get_balance('savings')}")
            except ValueError:
                print("   - Savings Account: Not Created")
            try:
                print(f"   - Checking Balance: ${account.customer.get_balance('checking')}")
            except ValueError:
                print("   - Checking Account: Not Created")
            input("\nPress Enter to go back to the menu...")

        elif choice == "2":
            print("\n💸 Withdraw Money")
            try:
                print("1. Withdraw from Savings")
                print("2. Withdraw from Checking")
                acc_choice = input("Choose an account: ")
                amount = float(input("Enter Amount to Withdraw: $"))
                if acc_choice == "1":
                    account.withdraw(amount, "savings")
                elif acc_choice == "2":
                    account.withdraw(amount, "checking")
                else:
                    print("\n❌ Invalid Choice. Returning to Menu.")
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\nPress Enter to go back to the menu...")

        elif choice == "3":
            print("\n💰 Deposit Money")
            try:
                print("1. Deposit to Savings")
                print("2. Deposit to Checking")
                acc_choice = input("Choose an account: ")
                amount = float(input("Enter Amount to Deposit: $"))
                if acc_choice == "1":
                    account.deposit(amount, "savings")
                elif acc_choice == "2":
                    account.deposit(amount, "checking")
                else:
                    print("\n❌ Invalid Choice. Returning to Menu.")
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\nPress Enter to go back to the menu...")

        elif choice == "4":
            print("\n🔄 Transfer Money")
            try:
                print("1. Transfer from Savings to Checking")
                print("2. Transfer from Checking to Savings")
                print("3. Transfer to Another Customer")
                acc_choice = input("Choose an option: ")
                amount = float(input("Enter Amount to Transfer: $"))
                if acc_choice == "1":
                    account.transfer(amount, "savings", "checking")
                elif acc_choice == "2":
                    account.transfer(amount, "checking", "savings")
                elif acc_choice == "3":
                    receiver_id = input("Enter Receiver's Account ID: ")
                    account.transfer(amount, "checking", "checking", receiver_id)
                else:
                    print("\n❌ Invalid Choice. Returning to Menu.")
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\nPress Enter to go back to the menu...")

        elif choice == "5":
            print("\n🏦 Create Savings / Checking Account")
            print("1. Create Savings Account")
            print("2. Create Checking Account")
            acc_choice = input("Choose an option: ")
            try:
                if acc_choice == "1":
                    account.customer.create_account("savings")
                    print("\n✅ Savings Account Created Successfully!")
                elif acc_choice == "2":
                    account.customer.create_account("checking")
                    print("\n✅ Checking Account Created Successfully!")
                else:
                    print("\n❌ Invalid Choice. Returning to Menu.")
            except ValueError as e:
                print(f"\n❌ {e}")
            input("\nPress Enter to go back to the menu...")

        elif choice == "6":
            print("\n✅ Logging Out... Thank You for Banking with ACME!\n")
            break
        else:
            print("\n❌ Invalid Choice. Please Try Again.")

if __name__ == "__main__":
    main()