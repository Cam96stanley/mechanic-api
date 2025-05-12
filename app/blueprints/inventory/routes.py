from flask import jsonify, request
from sqlalchemy import select
from marshmallow import ValidationError
from app.blueprints.inventory import inventory_bp
from app.models import db
from app.models import Inventory
from app.blueprints.inventory.schemas import inventory_item_schema, inventory_items_schema

# Create Inventory Item
@inventory_bp.route("/", methods=["POST"])
def create_inventory_item():
  try:
    item_data = inventory_item_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  new_item = Inventory(item_name=item_data["item_name"], item_price=item_data["item_price"])
  
  db.session.add(new_item)
  db.session.commit()
  
  return inventory_item_schema.jsonify(new_item), 201

# Get All Inventory Items
@inventory_bp.route("/", methods=["GET"])
def get_all_inventory():
  query = select(Inventory)
  inventory = db.session.execute(query).scalars().all()
  
  if not inventory:
    return jsonify({"message": "No items in inventory"}), 400
  
  return inventory_items_schema.jsonify(inventory), 200

# Get Inventory Item
@inventory_bp.route("/<int:item_id>", methods=["GET"])
def get_item(item_id):
  query = select(Inventory).where(Inventory.id == item_id)
  item = db.session.execute(query).scalars().first()
  
  if not item:
    return jsonify({"message": "No item with that id"}), 404
  
  return inventory_item_schema.jsonify(item), 200

# Update Item
@inventory_bp.route("/<int:item_id>", methods=["PUT"])
def update_item(item_id):
  query = select(Inventory).where(Inventory.id == item_id)
  item = db.session.execute(query).scalars().first()
  
  if item == None:
    return jsonify({"message": "No item with that id"}), 404
  
  try:
    item_data = inventory_item_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  for field, value in item_data.items():
    setattr(item, field, value)
  
  db.session.commit()
  
  return inventory_item_schema.jsonify(item), 200

# Delete Inventory Item
@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
  query = select(Inventory).where(Inventory.id == item_id)
  item = db.session.execute(query).scalars().first()
  
  db.session.delete(item)
  db.session.commit()
  
  return jsonify({"message": f"successfully deleted item {item_id}"})