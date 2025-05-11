from app.extensions import ma
from app.models import Service_Ticket, Ticket_Inventory
from marshmallow import fields

class AddTicketPartSchema(ma.Schema):
  '''
    total: 100.00,
    ticket: {
      ticket_id: 1,
      customer_id: 1
      vin: "asdfjkl;asdfjkl;",
      service_desc: "change flat tire",
      service_date: 2025-05-08
      ticket_parts: [
        {
          part: {
            item_name: "tire",
            price: 100.00,
          },
          quantity: 1,
        },
      ],
    }
  '''
  total = fields.Float(required=True)
  ticket_parts = fields.Nested("TicketInventorySchema")
  

class TicketInventorySchema(ma.SQLAlchemyAutoSchema):
  part = fields.Nested("InventorySchema")
  inventory = fields.Nested("InventorySchema")
  class Meta:
    model = Ticket_Inventory
    include_fk = True
    fields = ("inventory_id", "service_ticket_id", "quantity", "part", "inventory")
    
  

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
  mechanics = fields.Nested("MechanicSchema", many=True)
  customer = fields.Nested("CustomerSchema")
  tickets_inventory = fields.Nested(TicketInventorySchema, many=True)
  class Meta:
    model = Service_Ticket
    fields = ("mechanic_ids", "vin", "service_date", "service_desc", "customer_id", "mechanics", "customer", "id", "tickets_inventory")
    

class EditTicketSchema(ma.Schema):
  add_mechanic_ids = fields.List(fields.Int(), required=True)
  remove_mechanic_ids = fields.List(fields.Int(), required=True)
  class Meta:
    fields = ("add_mechanic_ids", "remove_mechanic_ids")
    
    
    
    
ticket_schema = ServiceTicketSchema()
tickets_schema = ServiceTicketSchema(many=True)
return_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])
return_tickets_schema = ServiceTicketSchema(many=True, exclude=["customer_id"])
my_tickets_schema = ServiceTicketSchema(many=True, exclude=["customer", "customer_id"])
edit_ticket_schema = EditTicketSchema()
add_ticket_part_schema = AddTicketPartSchema()