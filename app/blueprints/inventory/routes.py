from flask import request, jsonify
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema
from app.models import Inventory, db


# Create Inventory item
@inventory_bp.route("/", methods=["POST"])
def create_item():
  try:
    inventory_data = inventory_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  new_item = Inventory(item_name=inventory_data["item_name"], price=inventory_data["price"])
  
  db.session.add(new_item)
  db.session.commit()
  
  return inventory_schema.jsonify(new_item), 201