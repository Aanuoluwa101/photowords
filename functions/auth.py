import json
import boto3
import base64
import hashlib
import hmac
from botocore.exceptions import ClientError
import os 

# Initialize the Cognito client
client = boto3.client('cognito-idp', region_name='eu-west-2')

# Replace these with your actual User Pool ID and Client ID
USER_POOL_ID = 'eu-west-2_rJYXgTcQp'
CLIENT_ID = os.getenv('client_id')
CLIENT_SECRET = os.getenv('client_secret')


def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2

def sign_up():
    try:
        username = 'username'
        password = '1234'
        # Sign up the user using Cognito
        response = client.sign_up(
            ClientId=CLIENT_ID,
            SecretHash=get_secret_hash(username),
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',  # Add email as a required attribute
                    'Value': f'{username}@photowords.com'  # Assuming username is an email
                }
            ]
        )

        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User signed up successfully!',
                'userSub': response['UserSub']  # Cognito-generated unique ID for the user
            })
        }

    except ClientError as e:
        # Handle errors from Cognito
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': e.response['Error']['Message']
            })
        }
    except Exception as e:
        # Handle other errors
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
    
print(sign_up())