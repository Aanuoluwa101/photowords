from redis_client import ElastiCacheIAMProvider
import json
from datetime import datetime, timezone
import os
import boto3 
import random
import uuid
import redis


ATTEMPTS_DYNAMODB_TABLE = os.environ['ATTEMPTS_DYNAMODB_TABLE']

dynamodb = boto3.resource('dynamodb')

username = "photowords-redis" 
cache_name = "photowords-redis-cluster"
elasticache_endpoint = "master.photowords-redis-cluster.i82bzn.euw2.cache.amazonaws.com" 
creds_provider = ElastiCacheIAMProvider(user=username, cache_name=cache_name, is_serverless=False)
redis_client = redis.Redis(host=elasticache_endpoint, port=6379, credential_provider=creds_provider, ssl=True, ssl_cert_reqs="none", decode_responses=True)


def lambda_handler(event, context): 
    try:
        game_attempt_id = event['pathParameters']["game_attempt_id"]
        game_attempt = redis_client.get(game_attempt_id)
        if not game_attempt:
            raise ValueError("Game attempt not found")
        
        game_attempt = json.loads(game_attempt)
        redis_client.delete(game_attempt_id)

        # update game attempt in database
        attempts_table = dynamodb.Table(ATTEMPTS_DYNAMODB_TABLE)
        attempts_table.update_item(
            Key={'id': game_attempt_id},
            AttributeUpdates={
                'finished_at': {'Value': datetime.now(timezone.utc).isoformat()},
                'answers': {'Value': game_attempt['answers']}
            }
        )

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Game finished",
                "game_attempt": game_attempt_id
            })
        }
    except Exception as e: 
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }  