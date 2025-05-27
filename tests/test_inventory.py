from app import create_app
from app.models import db, Inventory
import unittest

class TestMechanic(unittest.TestCase):
  def setUp(self):
    self.app = create_app("TestingConfig")
    self.app_context = self.app.app_context()
    self.app_context.push()
    with self.app.app_context():
      db.drop_all()
      db.create_all()
      self.item = Inventory(item_name="windshield wiper", item_price=20.00)
      db.session.add(self.item)
      db.session.commit()
    self.client = self.app.test_client()
    
  def tearDown(self):
    db.session.remove()
    db.engine.dispose()
    self.app_context.pop()
    
  def test_item_creation(self):
    item_payload = {
      "item_name": "brake pads",
      "item_price": 49.99
    }
    
    response = self.client.post("/inventory/", json=item_payload)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.json["item_name"], "brake pads")
    
  def test_invalid_item_creation(self):
    item_payload = {
      "item_name": "engine"
    }
    
    response = self.client.post("/inventory/", json=item_payload)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json["item_price"], ["Missing data for required field."])
    
  def test_update_item(self):
    update_payload = {
      "item_name": "mustang engine",
      "item_price": 2000.00
    }
    
    response = self.client.put("/inventory/1", json=update_payload)
    self.assertEqual(response.json["item_name"], "mustang engine")
    self.assertEqual(response.json["item_price"], 2000.00)
    
  def test_get_items(self):
    response = self.client.get("/inventory/")
    
    self.assertEqual(response.status_code, 200)
    data = response.json
    self.assertIsInstance(data, list)
    
    self.assertGreaterEqual(len(data), 1)
    
    first_item = data[0]
    self.assertIn("item_name", first_item)
    self.assertIn("item_price", first_item)
    
  def test_get_item(self):
    response = self.client.get("/inventory/1")
    
    self.assertEqual(response.status_code, 200)
    item_data = response.json
    
    self.assertEqual(item_data["item_name"], "windshield wiper")
    self.assertEqual(item_data["item_price"], 20.00)
    
  def test_get_item_not_found(self):    
    response = self.client.get("/inventory/9999")
    
    self.assertEqual(response.status_code, 404)
    self.assertIn("message", response.json)
    self.assertEqual(response.json["message"], "No item with that id")
    
  def test_delete_item(self):
    payload = {
      "item_name": "spark plug",
      "item_price": 19.99
    }
    
    self.client.post("/inventory/", json=payload)
    
    delete_response = self.client.delete("/inventory/1")
    
    self.assertEqual(delete_response.status_code, 200)