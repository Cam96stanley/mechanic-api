from flask import request, jsonify
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, all_inventory_schema
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

# Get All Invenory
@inventory_bp.route("/", methods=["GET"])
def get_inventory():
  query = select(Inventory)
  inventory = db.session.execute(query).scalars().all()
  return all_inventory_schema.jsonify(inventory), 200

# Get Item from Inventory
@inventory_bp.route("/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
  query = select(Inventory).where(Inventory.id == item_id)
  item = db.session.execute(query).scalars().first()
  if not item:
    return jsonify({"message": "invalid item id"}), 404
  else:
    return inventory_schema.jsonify(item), 200
  
# Update inventory item
@inventory_bp.route("/<int:item_id>", methods=["PUT"])
def update_inventory_item(item_id):
  query = select(Inventory).where(Inventory.id == item_id)
  item = db.session.execute(query).scalars().first()
  
  if not item:
    return jsonify({"message": "invalid item id"}), 404
  
  try:
    item_data = inventory_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  for field, value in item_data.items():
    setattr(item, field, value)
  
  db.session.commit()
  return inventory_schema.jsonify(item), 200
  
# Delete item from inventory
@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
  query = select(Inventory).where(Inventory.id == item_id)
  item = db.session.execute(query).scalars().first()
  if not item:
    return jsonify({"message": "invalid item id"}), 404
  else:
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"successfully deleted item {item_id}"}), 200