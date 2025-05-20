from app import create_app
from app.models import db, Customer
import unittest
from app.utils.util import encode_token

class TestCustomer(unittest.TestCase):
  def setUp(self):
    self.app = create_app("TestingConfig")
    self.app_context = self.app.app_context()
    self.app_context.push()
    self.customer = Customer(customer_name="test_user", customer_email="test@email.com", customer_phone="7894561230", customer_password="test")
    with self.app.app_context():
      db.drop_all()
      db.create_all()
      db.session.add(self.customer)
      db.session.commit()
    self.token = encode_token(1)
    self.client = self.app.test_client()
    
  def tearDown(self):
    db.session.remove()
    db.engine.dispose()
    self.app_context.pop() 
    
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
    
  def test_invalid_customer_creation(self):
    customer_payload = {
      "customer_name": "John Doe",
      "customer_phone": "7851234688",
      "customer_password": "123"
    }
    
    response = self.client.post("/customers/", json=customer_payload)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json["customer_email"], ["Missing data for required field."])
    
  def test_login_customer(self):
    credentials = {
      "customer_email": "test@email.com",
      "customer_password": "test"
    }
    
    response = self.client.post("/customers/login", json=credentials)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json["status"], "success")
    return response.json["auth_token"]
  
  def test_invalid_login(self):
    credentials = {
      "customer_email": "bad_email@test.com",
      "customer_password": "bad_pw"
    }
    
    response = self.client.post("/customers/login", json=credentials)
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response.json["message"], "Invalid email or password")
    
  def test_update_customer(self):
    update_payload = {
      "customer_name": "John Doe",
      "customer_phone": "1234567890",
      "customer_email": "test@email.com",
      "customer_password": "123"
    }
    
    headers = {"Authorization": "Bearer " + self.test_login_customer()}
    
    response = self.client.put("/customers/", json=update_payload, headers=headers)
    self.assertEqual(response.json["customer_name"], "John Doe")
    self.assertEqual(response.json["customer_email"], "test@email.com")
    
  def test_get_customers(self):
    response = self.client.get("/customers/")
    
    self.assertEqual(response.status_code, 200)
    data = response.json
    self.assertIsInstance(data, list)
    
    self.assertGreaterEqual(len(data), 1)
    
    first_customer = data[0]
    self.assertIn("customer_name", first_customer)
    self.assertIn("customer_email", first_customer)
    self.assertIn("customer_phone", first_customer)
    
  def test_get_customer(self):
    response = self.client.get("/customers/1")
    
    self.assertEqual(response.status_code, 200)
    customer_data = response.json
    
    self.assertEqual(customer_data["customer_name"], "test_user")
    self.assertEqual(customer_data["customer_email"], "test@email.com")
    self.assertEqual(customer_data["customer_phone"], "7894561230")
    
  def test_get_customer_not_found(self):
    response = self.client.get("/customers/9999")
    
    self.assertEqual(response.status_code, 404)
    self.assertIn("message", response.json)
    self.assertEqual(response.json["message"], "Invalid customer id")
    
  def test_delete_customer(self):
    payload = {
      "customer_name": "Delete User",
      "customer_email": "delete_test@example.com",
      "customer_phone": "1234567890",
      "customer_password": "123"
    }
    
    self.client.post("/customers/", json=payload)
    
    login_response = self.client.post("/customers/login", json={
      "customer_email": "delete_test@example.com",
      "customer_password": "123"
    })
    token = login_response.json.get("auth_token")
    self.assertIsNotNone(token)
    
    headers = {"Authorization": f"Bearer {token}"}
    delete_response = self.client.delete("/customers/", headers=headers)
    
    self.assertEqual(delete_response.status_code, 200)
    
  def test_invalid_delete_customer(self):
    invalid_token = "Bearer this.is.an.invalid.token"
    
    headers = {
      "Authorization": invalid_token
    }
    
    response = self.client.delete("/customers/", headers=headers)
    
    self.assertEqual(response.status_code, 401)
    
    self.assertIn("message", response.json)
    self.assertIn("token", response.json["message"].lower())
    
  def test_delete_customer_missing_token(self):
    response = self.client.delete("/customers/")
    
    self.assertEqual(response.status_code, 401)
    self.assertIn("message", response.json)