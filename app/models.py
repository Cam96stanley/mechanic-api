from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from typing import List
from datetime import date

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

service_mechanics = db.Table(
  "service_mechanics",
  Base.metadata,
  db.Column("service_ticket_id", db.ForeignKey("service_tickets.id")),
  db.Column("mechanic_id", db.ForeignKey("mechanics.id"))
)

class Customer(Base):
  __tablename__ = "customers"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(db.String(100))
  email: Mapped[str] = mapped_column(db.String(100), unique=True)
  password: Mapped[str] = mapped_column(db.String(50))
  phone: Mapped[str] = mapped_column(db.String(20), unique=True)
  
  service_tickets: Mapped[List["Service_Ticket"]] = db.relationship(back_populates="customer", cascade="all, delete")
  
class Mechanic(Base):
  __tablename__ = "mechanics"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(db.String(100))
  email: Mapped[str] = mapped_column(db.String(150), unique=True)
  phone: Mapped[str] = mapped_column(db.String(20), unique=True)
  salary: Mapped[float]
  
  service_tickets: Mapped[List["Service_Ticket"]] = db.relationship(secondary=service_mechanics, back_populates="mechanics")
  
class Service_Ticket(Base):
  __tablename__ = "service_tickets"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  vin: Mapped[str] = mapped_column(db.String(100), unique=True)
  service_date: Mapped[date]
  service_desc: Mapped[str] = mapped_column(db.String(255))
  customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"))
  
  customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
  mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanics, back_populates="service_tickets")
  ticket_items: Mapped[List["TicketsInventory"]] = db.relationship(back_populates="service_tickets")
  
  
class Inventory(Base):
  __tablename__ = "items"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  item_name: Mapped[str] = mapped_column(db.String(150), nullable=False)
  price: Mapped[float]
  
  ticket_items: Mapped[List["TicketsInventory"]] = db.relationship(back_populates="item")
  

class TicketsInventory(Base):
  __tablename__ = "tickets_inventory"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  inventory_id: Mapped[int] = mapped_column(db.ForeignKey("items.id"), nullable=False)
  ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable=False)
  quantity: Mapped[int] = mapped_column(nullable=False)
  
  item: Mapped["Inventory"] = db.relationship(back_populates="tickets_inventory")
  