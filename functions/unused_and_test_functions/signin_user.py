import json
import boto3
import jwt
import datetime
import os
import binascii
import hashlib

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("photowords_users")

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")  

def verify_password(stored_hash: str, password_attempt: str) -> bool:
    """Verifies a password against a stored hash."""
    try:
        salt_hex, original_hash_hex = stored_hash.split(":")
        salt = binascii.unhexlify(salt_hex)
        attempt_hash = hashlib.pbkdf2_hmac('sha256', password_attempt.encode('utf-8'), salt, 100000, dklen=32)
        attempt_hash_hex = binascii.hexlify(attempt_hash).decode('utf-8')
        return attempt_hash_hex == original_hash_hex
    except (ValueError, binascii.Error):
        return False

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
    
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Username and password are required"}),
            }

        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("username").eq(username),
        )

        if not response["Items"]: # Check if any items were returned
            return {
                "statusCode": 401,
                "body": json.dumps({"message": "Invalid username or password"}),
            }

        user_item = response["Items"][0] # Get the first item from the returned list.
        stored_hash = user_item["password"]

        if verify_password(stored_hash, password):
            # Generate JWT token
            payload = {
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return {
                "statusCode": 200,
                "body": json.dumps({"token": token}),
            }
        else:
            return {
                "statusCode": 401,
                "body": json.dumps({"message": "Invalid username or password"}),
            }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid JSON in request body"}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)}),
        }