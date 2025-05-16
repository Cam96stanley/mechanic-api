from app.models import Mechanic
from app.extensions import ma

class MechanicSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Mechanic
    
    
class PublicMechanicSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Mechanic
    fields = ("mechanic_name", "id")
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
public_mechanic_schema = PublicMechanicSchema()