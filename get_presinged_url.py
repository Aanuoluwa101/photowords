import json
import boto3
import re
from datetime import datetime

s3_client = boto3.client('s3')
S3_BUCKET = 'photowords'

def lambda_handler(event, context):
    try:
        tag = event["queryStringParameters"].get("tag")
        if not tag:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Image tag is required'
                })
            }

        # Validate the tag (must be a single word)
        if not re.match(r'^\w+$', tag):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Tag must be a single word containing only letters, numbers, or underscores.'
                })
            }

        object_key = f"images/{tag}"
        try:
            s3_client.head_object(Bucket=S3_BUCKET, Key=object_key)
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'An image with the tag "{tag}" already exists.'
                })
            }
        except s3_client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code != '403' and error_code != '404':
                raise e

        expiration_time = 60  # URL valid for 1 minute
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
             Params={"Bucket": S3_BUCKET, "Key": object_key},
             ExpiresIn=expiration_time,
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Presigned url successfully generated',
                'presignedUrl': presigned_url
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

        