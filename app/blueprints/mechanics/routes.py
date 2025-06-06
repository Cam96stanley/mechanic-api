from flask import request, jsonify
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from app.models import Mechanic, db
from app.extensions import limiter, cache
from app.utils.util import token_required

# Create Mechanic
@mechanics_bp.route("/", methods=["POST"]) # Did not limit here because it is likely to be a protected internal route
def create_mechanic():
  try:
    mechanic_data = mechanic_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  new_mechanic = Mechanic(
                    mechanic_name=mechanic_data["mechanic_name"],
                    mechanic_email=mechanic_data["mechanic_email"],
                    mechanic_phone=mechanic_data["mechanic_phone"],
                    mechanic_salary=mechanic_data["mechanic_salary"]
                    )
  
  db.session.add(new_mechanic)
  db.session.commit()
  
  return mechanic_schema.jsonify(new_mechanic), 201

# Get All Mechanics
@mechanics_bp.route("/", methods=["GET"])
@cache.cached(timeout=60) # Caching for 60 seconds because management or HR may be pulling up all mechanics frequently for scheduling or HR purposes and mechanics probably wont be updated frequently so this makes sense. 
def get_mechanics():
  query = select(Mechanic)
  result = db.session.execute(query).scalars().all()
  return mechanics_schema.jsonify(result), 200

# Get Single Mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
def get_mechanic(mechanic_id):
  query = select(Mechanic).where(mechanic_id == Mechanic.id)
  mechanic = db.session.execute(query).scalars().first()
  
  if not mechanic:
    return jsonify({"message": "invalid mechanic id"}), 404
  
  return mechanic_schema.jsonify(mechanic), 200

# Update Mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
  query = select(Mechanic).where(mechanic_id == Mechanic.id)
  mechanic = db.session.execute(query).scalars().first()
  
  if mechanic == None:
    return jsonify({"message": "Invalid mechanic id"}), 404
  
  try:
    mechanic_data = mechanic_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  for field, value in mechanic_data.items():
    setattr(mechanic, field, value)
    
  db.session.commit()
  return mechanic_schema.jsonify(mechanic_data), 200

# Delete Mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
def delete_mechanic(mechanic_id):
  query = select(Mechanic).where(mechanic_id == Mechanic.id)
  mechanic = db.session.execute(query).scalars().first()
  if mechanic:
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"successfully deleted customer {mechanic_id}"}), 200
  else:
    return jsonify({"error": "customer not found"}), 404
  
# Sort Mechanics by Experience
@mechanics_bp.route("/experience", methods=["GET"])
def get_mechanics_experience():
  query = select(Mechanic)
  mechanics = db.session.execute(query).scalars().all()
  
  mechanics.sort(key = lambda mechanic: len(mechanic.service_tickets), reverse=True)
  
  return mechanics_schema.jsonify(mechanics), 200