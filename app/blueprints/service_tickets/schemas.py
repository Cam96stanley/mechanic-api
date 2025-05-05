from app.extensions import ma
from app.models import Service_Ticket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
  mechanics = fields.Nested("MechanicSchema", many=True)
  customer = fields.Nested("CustomerSchema")
  class Meta:
    model = Service_Ticket
    fields = ("mechanic_ids", "vin", "service_date", "service_desc", "customer_id", "mechanics", "customer", "id")
    
ticket_schema = ServiceTicketSchema()
tickets_schema = ServiceTicketSchema(many=True)
return_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])
return_tickets_schema = ServiceTicketSchema(many=True, exclude=["customer_id"])
my_tickets_schema = ServiceTicketSchema(many=True, exclude=["customer", "customer_id"])