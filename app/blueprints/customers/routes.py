from flask import request, jsonify
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from app.models import Customer, db
from app.extensions import cache, limiter
from app.utils.util import encode_token, token_required

# login
@customers_bp.route("/login", methods=["POST"])
def login():
  try:
    credentials = login_schema.load(request.json)
    username = credentials["email"]
    password = credentials["password"]
  except KeyError:
    return jsonify({"message": "Invalid payload, expecting username and password"}), 400
  
  query = select(Customer).where(Customer.email == username)
  customer = db.session.execute(query).scalar_one_or_none()
  
  if customer and customer.password == password:
    auth_token = encode_token(customer.id)
    
    response = {
      'status': 'success',
      'message': 'Successfully logged in',
      'auth_token': auth_token
    }
    return jsonify(response), 200
  else:
    return jsonify({'message': 'Invalid email or password'}), 401
  

# Create Customer
@customers_bp.route("/", methods=["POST"])
@limiter.limit("5/hour") # limiting to 5 per hour because their could be many new customers but mechanic shops generally don't have a ton of customers in an hour due to time.
def create_customer():
  try:
    customer_data = customer_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  new_customer = Customer(
                    name=customer_data["name"],
                    email=customer_data["email"],
                    password=customer_data["password"],
                    phone=customer_data["phone"]
                    )
  
  db.session.add(new_customer)
  db.session.commit()
  
  return customer_schema.jsonify(new_customer), 201

# Get All Customers
@customers_bp.route("/", methods=["GET"])
@cache.cached(timeout=60) # Cached for 60 seconds because the shop will likely need to pull up customers for appointments frequently and since this is not likely to be updated very frequently at a mechanic shop I think 60 seconds is a decent amount of time. Can easily be changed if it does become an issue. 
def get_customers():
  query = select(Customer)
  result = db.session.execute(query).scalars().all()
  return customers_schema.jsonify(result), 200

# Get Single Customer
@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
  query = select(Customer).where(customer_id == Customer.id)
  customer = db.session.execute(query).scalars().first()
  if customer == None:
    return jsonify({"message": "Invalid customer id"}), 404
  
  return customer_schema.jsonify(customer), 200

# Update Customer
@customers_bp.route("/", methods=["PUT"])
@token_required
def update_customer(customer_id):
  print(customer_id)
  query = select(Customer).where(Customer.id == int(customer_id))
  customer = db.session.execute(query).scalars().first()
  
  if customer == None:
    return jsonify({"message": "Invalid customer id"}), 404
  
  try:
    customer_data = customer_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  for field, value in customer_data.items():
    setattr(customer, field, value)
    
  db.session.commit()
  return customer_schema.jsonify(customer), 200

# Delete Customer
@customers_bp.route("/", methods=["DELETE"])
@token_required
def delete_customer(customer_id):
  query = select(Customer).where(Customer.id == int(customer_id))
  customer = db.session.execute(query).scalars().first()
  if customer:
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"successfully deleted customer {customer_id}"}), 200
  else:
    return jsonify({"error": "customer not found"}), 404
  
  