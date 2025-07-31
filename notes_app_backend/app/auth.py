import os
import datetime
import jwt
from functools import wraps
from flask import request, jsonify

# PUBLIC_INTERFACE
def create_access_token(user_id):
    """Generates a JWT access token."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    secret = os.getenv("JWT_SECRET", "super-secret") # Use env secret in prod
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

# PUBLIC_INTERFACE
def decode_access_token(token):
    """Validates and decodes a JWT."""
    secret = os.getenv("JWT_SECRET", "super-secret")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# PUBLIC_INTERFACE
def jwt_required(fn):
    """
    Decorator to enforce JWT authentication on Flask view.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Attach user_id to request context for downstream use
        request.user_id = payload["user_id"]
        return fn(*args, **kwargs)
    return wrapper

