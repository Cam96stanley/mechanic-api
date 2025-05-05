from flask import request, jsonify
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.blueprints.service_tickets import tickets_bp
from app.blueprints.service_tickets.schemas import ticket_schema, return_ticket_schema, return_tickets_schema, my_tickets_schema
from app.models import Mechanic, Service_Ticket, db
from app.extensions import cache
from app.utils.util import token_required

# Create Ticket
@tickets_bp.route("/", methods=["POST"]) # Did not limit here because this will likely be a protected internal route
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
  tickets = db.session.execute(query).scalars().all()
  return return_tickets_schema.jsonify(tickets), 200

# Get Single Ticket
@tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@cache.cached(timeout=60) # Caching for 60 seconds because during a mechanics work, they could need to pull up the ticket for the job often and updates probably would not happen frequently in this line of work. Can be updated as needed.
def get_ticket(ticket_id):
  query = select(Service_Ticket).where(Service_Ticket.id == ticket_id)
  ticket = db.session.execute(query).scalars().first()
  if not ticket:
    return jsonify({"message": "invalid ticket id"}), 404
  else:
    return return_ticket_schema.jsonify(ticket), 200
  
# Get Tickets for Customer
@tickets_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_customer_ticket(customer_id):
  query = select(Service_Ticket).where(Service_Ticket.customer_id == customer_id)
  my_tickets = db.session.execute(query).scalars().all()
  if not my_tickets:
    return jsonify({"message": "there are no tickets for this customer"}), 404
  else:
    return my_tickets_schema.jsonify(my_tickets), 200