import json
import boto3
import random
import datetime
import rsa
import base64
from botocore.exceptions import ClientError

# AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('photowords_images')

CLOUDFRONT_DIST = "https://d26z1cm3nkb7ze.cloudfront.net"  # Your CloudFront domain
PRIVATE_KEY_PATH = "/opt/cloudfront-key.pem"  # Store private key in Lambda layer
KEY_PAIR_ID = "0a7b2225-1137-49c7-9d6d-70d18e9328ee"  # Your CloudFront key pair ID


private_key = """
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDIlxIVrmirkblZ
-----END PRIVATE KEY-----
"""


# Function to generate a signed CloudFront URL
def generate_signed_url(object_key):
    expires = int((datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).timestamp())

    policy = {
        "Statement": [
            {
                "Resource": f"{CLOUDFRONT_DIST}/{object_key}",
                "Condition": {"DateLessThan": {"AWS:EpochTime": expires}}
            }
        ]
    }

    policy_str = json.dumps(policy, separators=(',', ':'))
    # private_key = rsa.PrivateKey.load_pkcs1(open(PRIVATE_KEY_PATH).read())
    private_key = rsa.PrivateKey.load_pkcs1(private_key)
    signature = base64.b64encode(rsa.sign(policy_str.encode(), private_key, 'SHA-1')).decode()

    signed_url = f"{CLOUDFRONT_DIST}/{object_key}?Expires={expires}&Signature={signature}&Key-Pair-Id={KEY_PAIR_ID}"
    return signed_url

# Lambda Handler
def lambda_handler(event, context):
    s3_key = "https://photowords.s3.amazonaws.com/images/admin2"
    signed_url = generate_signed_url(s3_key)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "signed_url": signed_url
        })
    }
