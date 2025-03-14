import base64
import datetime
import json

import boto3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

# ssm_client = boto3.client('ssm')

# CloudFront secret from SSM
# CF_SIGNED_URL_KEY_PAIR_ID = ssm_client.get_parameter(f"CF_SIGNED_URL_KEY_PAIR_ID")
CF_SIGNED_URL_KEY_PAIR_ID = "KT9L7TG62XJ70"
# CF_SIGNED_URL_PRIVATE_KEY = ssm_client.get_parameter(f"CF_SIGNED_URL_PRIVATE_KEY")

# key pair id is expected to be str
# private key is expected to be bytes

# fix possible escaped newlines
private_key = open('cloudfront-test-key.pem', 'r').read()

# CF_SIGNED_URL_PRIVATE_KEY = CF_SIGNED_URL_PRIVATE_KEY.replace(b'\\n', b'\n')
CF_SIGNED_URL_PRIVATE_KEY = private_key.replace(b'\\n', b'\n')


# or, define your own

def generate_cloudfront_signature(message: bytes, private_key: bytes):
    private_key_signer = serialization.load_pem_private_key(
        private_key,
        password=None,
        backend=default_backend()
    )
    return private_key_signer.sign(message, padding.PKCS1v15(), hashes.SHA1())


def make_cloudfront_policy(resource: str, expire_epoch_time: int):
    policy = {
        'Statement': [{
            'Resource': resource,
            'Condition': {
                'DateLessThan': {
                    'AWS:EpochTime': expire_epoch_time
                }
            }
        }]
    }
    return json.dumps(policy).replace(" ", "")


def url_base64_encode(data: bytes):
    return base64.b64encode(data).replace(b'+', b'-').replace(b'=', b'_').replace(b'/', b'~').decode('utf-8')


def url_base64_decode(data: bytes):
    return base64.b64encode(data).replace(b'-', b'+').replace(b'_', b'=').replace(b'~', b'/').decode('utf-8')


def generate_cloudfront_signed_url(url: str, expire_seconds: int):
    expire_epoch_time = (datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds)).timestamp()
    expire_epoch_time = int(expire_epoch_time)
    policy = make_cloudfront_policy(url, expire_epoch_time)
    signature = generate_cloudfront_signature(policy.encode('utf-8'), CF_SIGNED_URL_PRIVATE_KEY)

    signed_url = f"{url}?" \
                 f"Policy={url_base64_encode(policy.encode('utf-8'))}&" \
                 f"Signature={url_base64_encode(signature)}&" \
                 f"Key-Pair-Id={CF_SIGNED_URL_KEY_PAIR_ID}"

    return signed_url

def lambda_handler(event, context):
    url = "https://d26z1cm3nkb7ze.cloudfront.net/images/admin2"
    signed_url = generate_cloudfront_signed_url(url, 600)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "signed_url": signed_url
        })
    }