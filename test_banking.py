import unittest
from banking import Customer

class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.test_customer = Customer("10001", "John", "Doe", "password123")

    def test_authenticate_correct_password(self):
        self.assertTrue(self.test_customer.authenticate("password123"))

    def test_authenticate_wrong_password(self):
        self.assertFalse(self.test_customer.authenticate("wrongpass"))

    def test_get_checking_balance(self):
        self.test_customer.balance_checking = 500
        self.assertEqual(self.test_customer.get_balance("checking"), 500)

    def test_get_savings_balance(self):
        self.test_customer.balance_savings = 1000
        self.assertEqual(self.test_customer.get_balance("savings"), 1000)

    def test_update_checking_balance(self):
        self.test_customer.balance_checking = 500
        self.test_customer.update_balance("checking", 800)
        self.assertEqual(self.test_customer.get_balance("checking"), 800)

    def test_update_savings_balance(self):
        self.test_customer.balance_savings = 1000
        self.test_customer.update_balance("savings", 1500)
        self.assertEqual(self.test_customer.get_balance("savings"), 1500)

    def test_create_checking_account(self):
        self.test_customer.create_account("checking")
        self.assertEqual(self.test_customer.balance_checking, 0.0)

    def test_create_savings_account(self):
        self.test_customer.create_account("savings")
        self.assertEqual(self.test_customer.balance_savings, 0.0)

    def test_create_existing_account(self):
        self.test_customer.create_account("checking")
        with self.assertRaises(ValueError):
            self.test_customer.create_account("checking")

    def test_invalid_account_type(self):
        with self.assertRaises(ValueError):
            self.test_customer.get_balance("invalid")

if __name__ == '__main__':
    unittest.main()
