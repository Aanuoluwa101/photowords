import json
import boto3
import base64
import hashlib
import hmac
from botocore.exceptions import ClientError

# Initialize the Cognito client
client = boto3.client('cognito-idp', region_name='eu-west-2')

# Replace these with your actual User Pool ID and Client ID
USER_POOL_ID = 'eu-west-2_rJYXgTcQp'
CLIENT_ID = 'r8hr17c6mbsv3unesc4tcb2d5'
CLIENT_SECRET = 'f4m630ieadorunvqqaka49cr1mt8uotts9obnpnp59igls31989'


def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2


username = 'sabidev'
password = '1234'


def initiate_auth():
    secret_hash = get_secret_hash(username)
    try:
      resp = client.admin_initiate_auth(
                 UserPoolId=USER_POOL_ID,
                 ClientId=CLIENT_ID,
                 AuthFlow='USER_PASSWORD_AUTH',
                 AuthParameters={
                     'USERNAME': username,
                     'SECRET_HASH': secret_hash,
                     'PASSWORD': password,
                  })
    except client.exceptions.NotAuthorizedException:
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e.__str__()
    return resp, None

def sign_in():
    resp, msg = initiate_auth()
    if msg != None:
        return {'message': msg, 
              "error": True, "success": False, "data": None}
    if resp.get("AuthenticationResult"):
      return {'message': "success", 
               "error": False, 
               "success": True, 
               "data": {
               "id_token": resp["AuthenticationResult"]["IdToken"],
      "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
      "access_token": resp["AuthenticationResult"]["AccessToken"],
      "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
      "token_type": resp["AuthenticationResult"]["TokenType"]
            }}
    else: #this code block is relevant only when MFA is enabled
        return {"error": True, 
           "success": False, 
           "data": None, "message": None}
    
print(sign_in())