"""
This function returns a summary of the application: 
number of images, number of groups, number of active game attempts, 
and number of completed game attempts.
"""

import json
import os
import boto3
import redis
from redis_client import ElastiCacheIAMProvider

# Environment variables
DYNAMODB_IMAGES_TABLE = os.environ['IMAGES_DYNAMODB_TABLE']
DYNAMODB_GROUPS_TABLE = os.environ['GROUPS_DYNAMODB_TABLE']
DYNAMODB_ATTEMPTS_TABLE = os.environ['ATTEMPTS_DYNAMODB_TABLE']
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_CACHE_NAME = os.environ.get("REDIS_CACHE_NAME")

# AWS resources
dynamodb = boto3.resource('dynamodb')
images_table = dynamodb.Table(DYNAMODB_IMAGES_TABLE)
groups_table = dynamodb.Table(DYNAMODB_GROUPS_TABLE)
attempts_table = dynamodb.Table(DYNAMODB_ATTEMPTS_TABLE)

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
        # Number of images
        # Try Redis first, fallback to DynamoDB
        num_images = redis_client.scard('all_images')
        if num_images == 0:
            images_count = images_table.scan(Select='COUNT')
            num_images = images_count.get('Count', 0)

        # Number of groups
        group_keys = [key for key in redis_client.scan_iter("group:*")]
        num_groups = len(group_keys)
        if num_groups == 0:
            groups_count = groups_table.scan(Select='COUNT')
            num_groups = groups_count.get('Count', 0)

        # Game attempts: active and completed
        # DynamoDB scan with filter on status
        active_count = 0
        completed_count = 0
        response = attempts_table.scan(
            ProjectionExpression="#s",
            ExpressionAttributeNames={"#s": "status"}
        )
        for item in response.get('Items', []):
            status = item.get('status')
            if status == "ACTIVE":
                active_count += 1
            elif status == "COMPLETED":
                completed_count += 1

        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = attempts_table.scan(
                ProjectionExpression="#s",
                ExpressionAttributeNames={"#s": "status"},
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            for item in response.get('Items', []):
                status = item.get('status')
                if status == "ACTIVE":
                    active_count += 1
                elif status == "COMPLETED":
                    completed_count += 1

        return {
            "statusCode": 200,
            "body": json.dumps({
                "num_images": num_images,
                "num_groups": num_groups,
                "num_active_game_attempts": active_count,
                "num_completed_game_attempts": completed_count
            }),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        }