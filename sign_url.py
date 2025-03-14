# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.asymmetric import padding
# from botocore.signers import CloudFrontSigner
# import datetime


# def rsa_signer(message):
#     private_key = open('cloudfront-test-key.pem', 'r').read()
#     private_key = serialization.load_pem_private_key(
#         private_key,
#         password=None,
#         backend=default_backend()
#     )
#     return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())



import json
import datetime
import rsa
from botocore.signers import CloudFrontSigner



def rsa_signer(message):
    private_key = open('cloudfront-test-key.pem', 'r').read()
    return rsa.sign(message, rsa.PrivateKey.load_pkcs1(private_key), 'SHA-1')

def lambda_handler(event, context):
    url = "https://d26z1cm3nkb7ze.cloudfront.net/images/admin2"
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    key_id = "KT9L7TG62XJ70"
    cf_signer = CloudFrontSigner(key_id, rsa_signer)
    signed_url = cf_signer.generate_presigned_url(url, date_less_than=expires_at)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "signed_url": signed_url
        })
    }
