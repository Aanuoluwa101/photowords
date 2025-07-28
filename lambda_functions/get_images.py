"""
This function retrieves a list of image tags from a Redis cache 
for fast access. If the cache is empty, it fetches the tags 
from a DynamoDB table, stores them in Redis, and then returns them.
"""



import json
import redis
import os
import boto3
from redis_client import ElastiCacheIAMProvider



dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])


# Redis Setup
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
        cache_key = "all_images"
        images = list(redis_client.smembers(cache_key))
        if not images:
            response = table.scan(
                ProjectionExpression='tag'
            )
            tags = [item['tag'] for item in response.get('Items', [])]
            if tags:
                redis_client.sadd(cache_key, *tags)
            images = tags
        return {
            "statusCode": 200,
            "body": json.dumps({"images": images})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
