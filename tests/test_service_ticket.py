from datetime import date, datetime, timedelta
from app import create_app
from app.models import db, Service_Ticket, Mechanic, Customer, Inventory
import unittest
from jose import jwt

class TestMechanic(unittest.TestCase):
  def setUp(self):
    self.app = create_app("TestingConfig")
    self.app_context = self.app.app_context()
    self.app_context.push()
    with self.app.app_context():
      db.drop_all()
      db.create_all()
      customer = Customer(customer_name="John Doe", customer_email="jdoe@test.com", customer_password="test123", customer_phone="4567891230", id=1)
      db.session.add(customer)
      mechanic1 = Mechanic(mechanic_name="Jane Wrench", mechanic_email="jwrench@test.com", mechanic_salary=60000, mechanic_phone="5467981302", id=1)
      mechanic2 = Mechanic(mechanic_name="Bob Bolt", mechanic_email="bbolt@test.com", mechanic_salary=60000, mechanic_phone="8467942031", id=2)
      db.session.add_all([customer, mechanic1, mechanic2])
      self.ticket = Service_Ticket(vin="351as3d15v3a5s1d351531sd", service_date=date(2025, 5, 20), service_desc="change break pads", customer_id=1, mechanics=[mechanic1])
      db.session.add(self.ticket)
      self.item = Inventory(item_name="windshield wiper", item_price=20.00)
      db.session.add(self.item)
      db.session.commit()
    self.client = self.app.test_client()
    
  def tearDown(self):
    db.session.remove()
    db.engine.dispose()
    self.app_context.pop()
    
  def test_ticket_creation(self): 
    ticket_payload = {
      "vin": ";asldkncqw;oenf;alwng;qlwn",
      "service_date": "2025-05-27",
      "service_desc": "change windshield wipers",
      "customer_id": 1,
      "mechanic_ids": [1]
    }
    
    response = self.client.post("/tickets/", json=ticket_payload)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.json["vin"], ";asldkncqw;oenf;alwng;qlwn")
    
  def test_invalid_ticket_creation_test(self):
    ticket_payload = {
        "service_date": "2025-05-27",
        "service_desc": "change windshield wipers",
        "customer_id": 1,
        "mechanic_ids": [1]
    }
    
    response = self.client.post("/tickets/", json=ticket_payload)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json["vin"], ["Missing data for required field."])
    
  def test_update_mechanic_on_ticket(self):
    update_payload = {
        "add_mechanic_ids": [2],
        "remove_mechanic_ids": [1]
    }
    
    response = self.client.put("/tickets/1/edit", json=update_payload)

    self.assertEqual(response.status_code, 200)
    self.assertIn("message", response.json)
    self.assertIn("Mechanics successfully updated for ticket", response.json["message"])
    
  def test_get_tickets(self):
    response = self.client.get("/tickets/")
    
    self.assertEqual(response.status_code, 200)
    data = response.json
    self.assertIsInstance(data, list)
    
    self.assertGreaterEqual(len(data), 1)
    
    first_ticket = data[0]
    self.assertIn("vin", first_ticket)
    self.assertIn("service_date", first_ticket)
    self.assertIn("service_desc", first_ticket)
    
  def test_get_ticket(self):
    credentials = {
      "customer_email": "jdoe@test.com",
      "customer_password": "test123"
    }
    
    login_response = self.client.post("/customers/login", json=credentials)
    self.assertEqual(login_response.status_code, 200)
    token = login_response.json["auth_token"]
    self.assertIsNotNone(token)

    headers = {
      "Authorization": f"Bearer {token}"
    }
    
    tickets_response = self.client.get("/tickets/my-tickets", headers=headers)
    
    self.assertEqual(tickets_response.status_code, 200)
    
  def test_add_ticket_item(self):
    with self.app.app_context():
      self.ticket = db.session.merge(self.ticket)
      ticket_id = self.ticket.id
    
    item_data = {
      "inventory_id": 1,
      "quantity": 2
    }
    
    response = self.client.post(f"/tickets/{ticket_id}", json=item_data)
    
    self.assertEqual(response.status_code, 201)