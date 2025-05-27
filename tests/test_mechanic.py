from app import create_app
from app.models import db, Mechanic, Service_Ticket
from datetime import date
import unittest

class TestMechanic(unittest.TestCase):
  def setUp(self):
    self.app = create_app("TestingConfig")
    self.app_context = self.app.app_context()
    self.app_context.push()
    self.mechanic = Mechanic(mechanic_name="test_mechanic", mechanic_email="test@email.com", mechanic_phone="7894561230", mechanic_salary=60000)
    with self.app.app_context():
      db.drop_all()
      db.create_all()
      db.session.add(self.mechanic)
      db.session.commit()
    self.client = self.app.test_client()
    
  def tearDown(self):
    db.session.remove()
    db.engine.dispose()
    self.app_context.pop()
    
  def test_create_mechanic(self):
    mechanic_payload = {
      "mechanic_name": "John Doe",
      "mechanic_email": "jdoe@example.com",
      "mechanic_phone": "1234567890",
      "mechanic_salary": 60000
    }
    
    response = self.client.post("/mechanics/", json=mechanic_payload)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.json["mechanic_name"], "John Doe")
    
  def test_invalid_mechanic_creation(self):
    mechanic_payload = {
      "mechanic_name": "John Doe",
      "mechanic_phone": "7851234688",
      "mechanic_salary": 60000
    }
    
    response = self.client.post("/mechanics/", json=mechanic_payload)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json["mechanic_email"], ["Missing data for required field."])
    
  def test_update_mechanic(self):
    update_payload = {
      "mechanic_name": "John Doe",
      "mechanic_phone": "1234567890",
      "mechanic_email": "test@email.com",
      "mechanic_salary": 60000
    }
    
    response = self.client.put("/mechanics/1", json=update_payload)
    self.assertEqual(response.json["mechanic_name"], "John Doe")
    self.assertEqual(response.json["mechanic_email"], "test@email.com")
    
  def test_get_mechanics(self):
    response = self.client.get("/mechanics/")
    
    self.assertEqual(response.status_code, 200)
    data = response.json
    self.assertIsInstance(data, list)
    
    self.assertGreaterEqual(len(data), 1)
    
    first_mechanic = data[0]
    self.assertIn("mechanic_name", first_mechanic)
    self.assertIn("mechanic_email", first_mechanic)
    self.assertIn("mechanic_phone", first_mechanic)
    
  def test_get_mechanic(self):
    response = self.client.get("/mechanics/1")
    
    self.assertEqual(response.status_code, 200)
    mechanic_data = response.json
    
    self.assertEqual(mechanic_data["mechanic_name"], "test_mechanic")
    self.assertEqual(mechanic_data["mechanic_email"], "test@email.com")
    self.assertEqual(mechanic_data["mechanic_phone"], "7894561230")
    
  def test_get_mechanic_not_found(self):
    response = self.client.get("/mechanics/9999")
    
    self.assertEqual(response.status_code, 404)
    self.assertIn("message", response.json)
    self.assertEqual(response.json["message"], "invalid mechanic id")
    
  def test_get_mechanics_by_experience(self):
    mechanic1 = Mechanic(mechanic_name="Alpha", mechanic_email="alpha@example.com", mechanic_phone="4444455555", mechanic_salary=60000)
    mechanic2 = Mechanic(mechanic_name="Beta", mechanic_email="beta@example.com", mechanic_phone="1234567890", mechanic_salary=60000)
    db.session.add_all([mechanic1, mechanic2])
    db.session.commit()

    ticket1 = Service_Ticket(service_desc="Fix brakes", vin="46546541516a4sdasdf4a65sd6", service_date=date(2025, 5, 20), customer_id=1, mechanics=[mechanic2])
    ticket2 = Service_Ticket(service_desc="Fix engine", vin="5646a5s4dasdvasdvas78", service_date=date(2025, 5, 16), customer_id=1, mechanics=[mechanic2])
    ticket3 = Service_Ticket(service_desc="Oil change", vin="sdfasd488465a1sd516416vsv", service_date=date(2025, 5, 18), customer_id=1, mechanics=[mechanic1])
    db.session.add_all([ticket1, ticket2, ticket3])
    db.session.commit()

    response = self.client.get("/mechanics/experience")
    
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response.json, list)

    self.assertGreaterEqual(len(response.json), 2)
    self.assertEqual(response.json[0]["mechanic_email"], "beta@example.com")
    self.assertEqual(response.json[1]["mechanic_email"], "alpha@example.com")
    
  def test_delete_mechanic(self):
    response = self.client.delete("/mechanics/1")
    self.assertEqual(response.status_code, 200)
    