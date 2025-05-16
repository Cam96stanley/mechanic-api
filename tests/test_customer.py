from app import create_app
from app.models import db, Customer
import unittest
from app.utils.util import encode_token

class TestCustomer(unittest.TestCase):
  def setUp(self):
    self.app = create_app("TestingConfig")
    self.customer = Customer(customer_name="test_user", customer_email="test@email.com", customer_phone="7894561230", customer_password="test")
    with self.app.app_context():
      db.drop_all()
      db.create_all()
      db.session.add(self.customer)
      db.session.commit()
    self.token = encode_token(1)
    self.client = self.app.test_client()
    
  def test_create_customer(self):
    customer_payload = {
      "customer_name": "John Doe",
      "customer_email": "jdoe@example.com",
      "customer_phone": "1234567890",
      "customer_password": "123"
    }
    
    response = self.client.post("/customers/", json=customer_payload)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.json["customer_name"], "John Doe")
    
  def test_login_customer(self):
    credentials = {
      "customer_email": "test@email.com",
      "customer_password": "test"
    }
    
    response = self.client.post("/customers/login", json=credentials)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json["status"], "success")
    return response.json["auth_token"]