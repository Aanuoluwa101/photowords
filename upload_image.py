import json
import boto3
import base64
import re
import uuid
from datetime import datetime

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

S3_BUCKET = 'photowords'
DYNAMODB_TABLE = 'photowords_images'

def lambda_handler(event, context):
    try:
        tag = event['headers'].get('tag')
        if not tag:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Tag header is required.'
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

        # Check if the body is base64-encoded (API Gateway encodes binary data as base64)
        if event['isBase64Encoded']:
            file_content = base64.b64decode(event['body'])  
        else:
            file_content = event['body']  

        s3_key = f"client/{tag}"
        try:
            s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
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

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentType=event['headers'].get('Content-Type', 'image/jpeg')
        )

        s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(
            Item={
                'id': str(uuid.uuid4()),  
                'tag': tag,
                'file_size': len(file_content),
                's3_url': s3_url,
                'upload_date': datetime.utcnow().isoformat()
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image uploaded successfully!',
                's3Url': s3_url
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

        