from datetime import datetime, timedelta, timezone
from jose import jwt
from functools import wraps
from flask import request, jsonify
from sqlalchemy import select
from app.models import db, Customer
import jose

SECRET_KEY = "a super duper, uber, incredibly long, secret key"

def encode_token(customer_id):
  payload = {
    'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
    'iat': datetime.now(timezone.utc),
    'sub': str(customer_id)
  }
  
  token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
  return token

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None
    
    if 'Authorization' in request.headers:
      token = request.headers['Authorization'].split()[1]
      
    if not token:
      return jsonify({"message": "Token is missing"}), 401
    
    try:
      data = jwt.decode(token, SECRET_KEY, algorithms='HS256')
      customer_id = data['sub']
      
      customer = db.session.execute(select(Customer).where(Customer.id == int(customer_id))).scalar_one_or_none()
      if not customer:
        return jsonify({"message": "Invalid credentials. Please log in again"}), 401
      
    except jose.exceptions.ExpiredSignatureError:
      return jsonify({"message": "Token has expired"}), 401
    except jose.exceptions.JWTError:
      return jsonify({"message": "Invalid token"}), 401
    
    return f(customer_id, *args, **kwargs)
  
  return decorated      
    