"""
This function creates a new game attempt for a user. 
It fetches all groups (questions) from Redis or DynamoDB, 
shuffles them, and selects a subset if a count is provided. 
It then generates a unique attempt ID, saves the attempt details 
to DynamoDB, caches the attempt in Redis for 1 day, and returns the 
attempt data in the response.
"""


from redis_client import ElastiCacheIAMProvider
import json
from datetime import datetime, timezone
import os
import boto3 
import random
import uuid
import redis
from decimal import Decimal



GROUPS_DYNAMODB_TABLE = os.environ['GROUPS_DYNAMODB_TABLE']
ATTEMPTS_DYNAMODB_TABLE = os.environ['ATTEMPTS_DYNAMODB_TABLE']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(GROUPS_DYNAMODB_TABLE)

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


class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)
  

def cache_group(group):
    group_id = group['id']
    redis_client.set(f"group:{group_id}", json.dumps(group, cls=DecimalEncoder))

def fetch_all_groups():
    try:
        keys = [key for key in redis_client.scan_iter("group:*")]
        if not keys:
            # Cache miss: load from DynamoDB
            scan_kwargs = {}
            all_groups = []
            done = False
            start_key = None

            while not done:
                if start_key:
                    scan_kwargs['ExclusiveStartKey'] = start_key
                response = table.scan(**scan_kwargs)
                for item in response.get('Items', []):
                    cache_group(item)
                    all_groups.append(item)
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None

            return all_groups

        # MGET to fetch all values at once
        raw_groups = redis_client.mget(keys)
        groups = [json.loads(group) for group in raw_groups if group]
        return groups

    except Exception as e:
        raise Exception(f"Error fetching all groups: {str(e)}")


def lambda_handler(event, context): 
    try:
        body = json.loads(event['body']) 
        username = body["username"] # body will be validated by api gateway 
        count =  body.get('count')
        created_at = datetime.now(timezone.utc).isoformat()
        groups = fetch_all_groups()
        random.shuffle(groups)
        attempt_id = str(uuid.uuid4())

        if count:
            groups = groups[:count]

        attempt = {
            "id": attempt_id,
            "username": username, 
            "created_at": created_at,
            "no_of_questions": len(groups),
            # maybe we do this "questions": [group.id for group in groups]
            "status": "ACTIVE"
        }  
        # save to db
        attempts_table = dynamodb.Table(ATTEMPTS_DYNAMODB_TABLE)
        attempts_table.put_item(Item=attempt)
        attempt["questions"] = groups
        
        # cache the data
        redis_client.set(f"attempt:{attempt_id}", json.dumps(attempt), ex=86400)  # 1 day
        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Game attempt successfully created",
                "game_attempt": attempt
            }),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        }
    except Exception as e: 
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }  