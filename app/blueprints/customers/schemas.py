from app.models import Customer
from app.extensions import ma

class CustomerSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Customer
    include_fk = True
    

class PublicCustomerSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Customer
    fields = ("id", "customer_name", "customer_email", "customer_phone")
    
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(exclude=["customer_name", "customer_phone"])
public_customer_schema = PublicCustomerSchema()