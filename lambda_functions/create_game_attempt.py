from redis_client import ElastiCacheIAMProvider
import json
from datetime import datetime, timezone
import os
import boto3 
import random
import uuid
import redis


GROUPS_DYNAMODB_TABLE = os.environ['GROUPS_DYNAMODB_TABLE']
ATTEMPTS_DYNAMODB_TABLE = os.environ['ATTEMPTS_DYNAMODB_TABLE']

dynamodb = boto3.resource('dynamodb')

username = "photowords-redis" 
cache_name = "photowords-redis-cluster"
elasticache_endpoint = "master.photowords-redis-cluster.i82bzn.euw2.cache.amazonaws.com" 
creds_provider = ElastiCacheIAMProvider(user=username, cache_name=cache_name, is_serverless=False)
redis_client = redis.Redis(host=elasticache_endpoint, port=6379, credential_provider=creds_provider, ssl=True, ssl_cert_reqs="none", decode_responses=True)


def fetch_all_groups():
    try:
        groups_table = dynamodb.Table(GROUPS_DYNAMODB_TABLE)
        response = groups_table.get_item(Key={'id': 'all_groups'})
        if "Item" in response:
            return response["Item"]["groups"]
        else:
            raise ValueError("No groups found")
    except Exception as e:
        raise e


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
            "no_of_questions": len(groups)
        }  
        # save to db
        attempts_table = dynamodb.Table(ATTEMPTS_DYNAMODB_TABLE)
        attempts_table.put_item(Item=attempt)

        attempt.pop("no_of_questions")
        attempt["questions"] = groups

        # cache the data
        cache_data = {
            **attempt, 
            "answers": {}, 
            "last_activity": datetime.now(timezone.utc).isoformat()
        }  
        redis_client.set(attempt_id, json.dumps(cache_data))
        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Game attempt successfully created",
                "game_attempt": attempt
            })
        }
    except Exception as e: 
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }  