from app.extensions import ma
from app.models import Service_Ticket, Ticket_Inventory
from marshmallow import fields



class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
  mechanics = fields.Nested("PublicMechanicSchema", many=True)
  customer = fields.Nested("PublicCustomerSchema")
  service_items = fields.Nested("ServiceItemsSchema", many=True)
  class Meta:
    model = Service_Ticket
    fields = ("mechanic_ids", "vin", "service_date", "service_desc", "customer_id", "mechanics", "customer", "id", "tickets_inventory", "service_items")


class EditTicketSchema(ma.Schema):
  add_mechanic_ids = fields.List(fields.Int(), required=True)
  remove_mechanic_ids = fields.List(fields.Int(), required=True)
  class Meta:
    fields = ("add_mechanic_ids", "remove_mechanic_ids")


class ServiceItemsSchema(ma.SQLAlchemyAutoSchema):
  inventory = fields.Nested("InventorySchema")
  class Meta:
    model = Ticket_Inventory
    fields = ("id", "inventory_id", "quantity", "inventory")
    




ticket_schema = ServiceTicketSchema()
tickets_schema = ServiceTicketSchema(many=True)
return_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])
return_tickets_schema = ServiceTicketSchema(many=True, exclude=["customer_id"])
my_tickets_schema = ServiceTicketSchema(many=True, exclude=["customer", "customer_id"])
edit_ticket_schema = EditTicketSchema()
service_items_schema = ServiceItemsSchema()