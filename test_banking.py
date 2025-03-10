import unittest
from banking import Customer  
class TestCustomer(unittest.TestCase):

    def setUp(self):
        """Setup a test customer before each test"""
        self.test_customer = Customer("10001", "John", "Doe", "password123", 500, 1000)

    def test_authenticate_correct_password(self):
        """Test if authentication succeeds with correct password"""
        self.assertTrue(self.test_customer.authenticate("password123"))

    def test_authenticate_wrong_password(self):
        """Test if authentication fails with wrong password"""
        self.assertFalse(self.test_customer.authenticate("wrongpass"))

    def test_get_checking_balance(self):
        """Test retrieving the checking balance"""
        self.assertEqual(self.test_customer.get_balance("checking"), 500)

    def test_get_savings_balance(self):
        """Test retrieving the savings balance"""
        self.assertEqual(self.test_customer.get_balance("savings"), 1000)

    def test_update_checking_balance(self):
        """Test updating checking account balance"""
        self.test_customer.update_balance("checking", 800)
        self.assertEqual(self.test_customer.get_balance("checking"), 800)

    def test_update_savings_balance(self):
        """Test updating savings account balance"""
        self.test_customer.update_balance("savings", 1500)
        self.assertEqual(self.test_customer.get_balance("savings"), 1500)

    def test_invalid_account_type(self):
        """Test for invalid account type error"""
        with self.assertRaises(ValueError):
            self.test_customer.get_balance("invalid")

if __name__ == '__main__':
    unittest.main()