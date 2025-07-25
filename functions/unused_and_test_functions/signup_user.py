import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import secrets
import binascii
import hashlib

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("photowords_users")

def hash_password(password: str, provided_salt: bytes = None) -> str:
    """Hashes a password using PBKDF2 with a randomly generated or provided salt."""

    salt = provided_salt if provided_salt else secrets.token_bytes(16) 
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=32)  
    salt_hex = binascii.hexlify(salt).decode('utf-8')
    hash_hex = binascii.hexlify(dk).decode('utf-8')

    return f"{salt_hex}:{hash_hex}"

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
    
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            return {"statusCode": 400, "body": json.dumps({"message": "Username and password are required"})}

        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("username").eq(username),
        )
        if response["Items"]:
            return {"statusCode": 409, "body": json.dumps({"message": "Username already taken"})}

        hashed_password = hash_password(password) 
        print(hashed_password)

        table.put_item(Item={"username": username, "password": hashed_password})
        return {"statusCode": 201, "body": json.dumps({"message": "User created successfully"})}
    except (BotoCoreError, ClientError) as e:
        return {"statusCode": 500, "body": json.dumps({"message": "Internal Server Error", "error": str(e)})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": "Unexpected Error", "error": str(e)})}