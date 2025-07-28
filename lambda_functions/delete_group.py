"""
This function deletes a group by its ID from both DynamoDB and Redis cache. 
It expects the group ID as a query parameter, 
removes the group from the database and cache
"""

import json
import boto3
import os
import redis
from redis_client import ElastiCacheIAMProvider


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['GROUPS_DYNAMODB_TABLE'])

# Redis
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_CACHE_NAME = os.environ.get("REDIS_CACHE_NAME")

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
        group_id = event.get("queryStringParameters", {}).get("id")
        table.delete_item(Key={'id': group_id})
        redis_client.delete(f"group:{group_id}")

        return {
            'statusCode': 204,
            'body': json.dumps({
                'message': f'Group {group_id} deleted successfully!'
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }