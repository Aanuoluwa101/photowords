import json
import boto3
import re
import os
from datetime import datetime

s3_client = boto3.client('s3')
S3_BUCKET = os.environ['S3_BUCKET']
EXPIRATION_TIME = os.environ['S3_PRESIGNED_URL_EXPIRATION_TIME']

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)


def lambda_handler(event, context):
    try:
        # Extract and verify the tag parameter: it's more like the name of the image 
        params = event.get("queryStringParameters")
        if not params:            
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'tag parameter required'
                })
            }
        tag = params.get("tag")
        if not tag:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'tag parameter required'
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

        # check if s3 already contains an image with that tag
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

        # check if image exists in DB
        response = table.get_item(Key={'tag': tag})
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'An image with the tag "{tag}" is already exists'
                })
            }

        # generate and return presigned url that will last 5 minutes
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
             Params={"Bucket": S3_BUCKET, "Key": object_key},
             ExpiresIn=EXPIRATION_TIME,
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

        