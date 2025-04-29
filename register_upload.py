import json
import boto3
from datetime import datetime
import uuid
import os

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

S3_BUCKET = os.environ['S3_BUCKET']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']


def check_image_exists_in_db(pk_value):
    response = dynamodb_client.get_item(
        TableName=DYNAMODB_TABLE,
        Key={"tag": {"S": pk_value}}  
    )
    return "Item" in response

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        tag = body.get('tag')
        image_type = body.get('imageType')
        object_key = f"images/{tag}"
        try:
            s3_client.head_object(Bucket=S3_BUCKET, Key=object_key) # this will throw an error if not found
            if check_image_exists_in_db(tag):
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': f'An image with the tag "{tag}" already registered.'
                    })
                }
            s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{object_key}"
            cloudfront_url = f"https://d26z1cm3nkb7ze.cloudfront.net/images/{tag}"
            uploaded_at = datetime.utcnow().isoformat()
            dynamodb_client.put_item(
                TableName=DYNAMODB_TABLE,
                Item={
                    'tag': {"S": tag}, 
                    's3_url': {"S": s3_url},  
                    'cloudfront_url': {"S": cloudfront_url},  
                    'uploaded_at': {"S": uploaded_at},  
                    'image_type': {"S": image_type}
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Image upload successfully registered',
                    's3Url': s3_url,
                    'cloudfrontUrl': cloudfront_url,
                    'uploaded_at': uploaded_at,
                    'imageType': image_type
                })
            }
        except s3_client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '403' or error_code == '404':
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': f'An image with the tag "{tag}" does not exist.'
                    })
                }
            else: 
                raise e
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

        