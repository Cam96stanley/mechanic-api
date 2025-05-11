from flask import request, jsonify
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.blueprints.service_tickets import tickets_bp
from app.blueprints.service_tickets.schemas import ticket_schema, return_ticket_schema, return_tickets_schema, my_tickets_schema, edit_ticket_schema, add_ticket_part_schema
from app.models import Mechanic, Service_Ticket, Inventory, Ticket_Inventory, db
from app.extensions import cache
from app.utils.util import token_required

# Create Ticket
@tickets_bp.route("/", methods=["POST"]) # Did not limit here because this will likely be a protected internal route
def create_ticket():
  try:
    ticket_data = ticket_schema.load(request.json)
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
  
# Update mechanics on Ticket
@tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
def update_ticket_mechanics(ticket_id):
  try:
    ticket_edits = edit_ticket_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
    
  query = select(Service_Ticket).where(Service_Ticket.id == ticket_id)
  ticket = db.session.execute(query).scalars().first()
  
  for mechanic_id in ticket_edits["add_mechanic_ids"]:
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic and mechanic not in ticket.mechanics:
      ticket.mechanics.append(mechanic)
      
  for mechanic_id in ticket_edits["remove_mechanic_ids"]:
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic and mechanic in ticket.mechanics:
      ticket.mechanics.remove(mechanic)
      
  db.session.commit()
  return ticket_schema.jsonify(ticket), 200
      
# Add Part to Existing Ticket
@tickets_bp.route("/<int:ticket_id>", methods=["POST"])
def add_ticket_parts(ticket_id):
    data = request.get_json()
    ticket_parts = data.get("ticket_parts", [])
    
    ticket = db.session.get(Service_Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    total = 0

    for item in ticket_parts:
        part_data = item.get("part")
        quantity = item.get("quantity", 1)
        item_name = part_data.get("item_name")
        item_price = part_data.get("price")

        part = db.session.query(Inventory).filter_by(item_name=item_name).first()
        if not part:
        
            part = Inventory(item_name=item_name, item_price=item_price)
            db.session.add(part)
            db.session.flush()  

        ticket_inv = (
            db.session.query(Ticket_Inventory)
            .filter_by(service_ticket_id=ticket.id, inventory_id=part.id)
            .first()
        )
        if ticket_inv:
            ticket_inv.quantity += quantity
        else:
            ticket_inv = Ticket_Inventory(
                service_ticket_id=ticket.id,
                inventory_id=part.id,
                quantity=quantity
            )
            db.session.add(ticket_inv)

        total += part.item_price * quantity

    db.session.commit()

    calculated_total = sum(
        ti.inventory.item_price * ti.quantity for ti in ticket.tickets_inventory
    )

    result = return_ticket_schema.dump(ticket)
    result["total"] = calculated_total

    return jsonify(result), 201