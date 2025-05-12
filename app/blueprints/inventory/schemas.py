from app.models import Inventory
from app.extensions import ma

class InventorySchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Inventory

inventory_item_schema = InventorySchema()
inventory_items_schema = InventorySchema(many=True)