import json
import boto3
import os
import redis
from redis_client import ElastiCacheIAMProvider

S3_BUCKET = os.environ['S3_BUCKET']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_CACHE_NAME = os.environ.get("REDIS_CACHE_NAME")

# AWS resources
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

# Redis setup
creds_provider = ElastiCacheIAMProvider(
    user=REDIS_USERNAME,
    cache_name=REDIS_CACHE_NAME,
    is_serverless=False
)
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    credential_provider=creds_provider,
    ssl=True,
    ssl_cert_reqs="none",
    decode_responses=True
)

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters")
        if not params or "tag" not in params:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'tag parameter required'}), 
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            }
        tag = params["tag"]
        s3_key = f"images/{tag}" 

        # Delete from S3
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        except Exception as e:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Image not found in S3: {str(e)}'}), 
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            }

        # Delete from DynamoDB
        table.delete_item(Key={'tag': tag})

        # Remove from Redis cache
        redis_client.srem('all_images', tag)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Image "{tag}" deleted successfully.'}), 
            "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}), 
            "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
        }