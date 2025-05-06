from app.extensions import ma
from app.models import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Inventory
    
inventory_schema = InventorySchema()
all_inventory_schema = InventorySchema(many=True)
