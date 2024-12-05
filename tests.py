import os
import unittest
from dotenv import load_dotenv
from client import APIClient


class TestAPIClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load environment variables from .env file
        load_dotenv()
        base_url = os.getenv('API_BASE_URL')
        if not base_url:
            raise ValueError("API_BASE_URL environment variable not set in .env file")
        cls.client = APIClient(base_url=base_url)

        # Create a test user (ensure this user doesn't affect real data)
        cls.test_user_id = 231584958  # Use a unique Telegram ID for testing
        cls.test_user_data = {
            'telegram_id': cls.test_user_id,
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'language_code': 'en',
            'total_spent': 0,
            'balance': 99999,
            'banned': False
        }
        cls.client.create_or_update_user(cls.test_user_data)

    def test_ping(self):
        """Test the ping method."""
        result = self.client.ping()
        self.assertTrue(result)

    def test_get_nodes(self):
        """Test retrieving nodes."""
        nodes = self.client.get_nodes()
        self.assertIsInstance(nodes, list)

    def test_get_users(self):
        """Test retrieving users."""
        users = self.client.get_users(limit=5)
        self.assertIsInstance(users, list)
        self.assertLessEqual(len(users), 5)

    def test_create_or_update_user(self):
        """Test creating or updating a user."""
        user_data = {
            'telegram_id': self.test_user_id,
            'first_name': 'Updated',
            'last_name': 'User',
            'username': 'updateduser',
            'language_code': 'en',
            'banned': False
        }
        result = self.client.create_or_update_user(user_data)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['first_name'], 'Updated')

    def test_create_payment_ticket(self):
        """Test creating a payment ticket."""
        result = self.client.create_payment_ticket(user_id=self.test_user_id, amount=50.0)
        self.assertIsInstance(result, dict)
        self.assertIn('payment_ticket_id', result)
        self.payment_ticket_id = result['payment_ticket_id']

    def test_get_payments(self):
        """Test retrieving payments."""
        payments = self.client.get_payments(limit=5)
        self.assertIsInstance(payments, list)
        self.assertLessEqual(len(payments), 5)

    def test_complete_and_cancel_payment(self):
        """Test completing a payment."""
        # Create a new payment ticket
        result = self.client.create_payment_ticket(user_id=self.test_user_id, amount=25.0)
        payment_ticket_id = result['payment_ticket_id']
        # Complete the payment
        result = self.client.complete_payment(id_=payment_ticket_id)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('payment_ticket_id'), str(payment_ticket_id))

        # Cancel the payment
        result = self.client.cancel_payment(id_=payment_ticket_id)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('payment_ticket_id'), str(payment_ticket_id))
        self.assertEqual(result.get('status'), 'cancelled')


if __name__ == '__main__':
    unittest.main()
