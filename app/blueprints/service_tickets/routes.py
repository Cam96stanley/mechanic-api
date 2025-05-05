from flask import request, jsonify
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.blueprints.service_tickets import tickets_bp
from app.blueprints.service_tickets.schemas import ticket_schema, tickets_schema, return_ticket_schema, return_tickets_schema
from app.models import Mechanic, Service_Ticket, db

# Create Ticket
@tickets_bp.route("/", methods=["POST"])
def create_ticket():
  try:
    ticket_data = ticket_schema.load(request.json)
    print(ticket_data)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  new_ticket = Service_Ticket(vin=ticket_data["vin"], service_date=ticket_data["service_date"], service_desc=ticket_data["service_desc"], customer_id=ticket_data["customer_id"])
  
  for mechanic_id in ticket_data["mechanic_ids"]:
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalar()
    if mechanic:
      new_ticket.mechanics.append(mechanic)
    else:
      return jsonify({"message": "invlaid mechanic id"})
  
  db.session.add(new_ticket)
  db.session.commit()
  
  return return_ticket_schema.jsonify(new_ticket), 201

# Get All Tickets
@tickets_bp.route("/", methods=["GET"])
def get_tickets():
  query = select(Service_Ticket)
  result = db.session.execute(query).scalars().all()
  return return_tickets_schema.jsonify(result), 200