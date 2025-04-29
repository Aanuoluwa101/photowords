from redis_client import ElastiCacheIAMProvider
import json
import redis


username = "photowords-redis" 
cache_name = "photowords-redis-cluster"
elasticache_endpoint = "master.photowords-redis-cluster.i82bzn.euw2.cache.amazonaws.com" 
creds_provider = ElastiCacheIAMProvider(user=username, cache_name=cache_name, is_serverless=False)
redis_client = redis.Redis(host=elasticache_endpoint, port=6379, credential_provider=creds_provider, ssl=True, ssl_cert_reqs="none", decode_responses=True)



def lambda_handler(event, context): 
    try:
        # body = event['body']
        # game_attempt_id = event['pathParameters']["game_attempt_id"]
        body = json.loads(event['body']) 
        game_attempt_id = event['pathParameters']["game_attempt_id"]

        game_attempt = redis_client.get(game_attempt_id)
        if not game_attempt:
            raise ValueError("Game attempt not found")

        game_attempt = json.loads(game_attempt)
        group_id = body['group_id']
        if group_id not in game_attempt['questions']:
            raise ValueError("Invalid group ID")
        
        if group_id in game_attempt['answers']:
            raise ValueError("Group already submitted")
        
        game_attempt['answers'][group_id] = body
        redis_client.set(game_attempt_id, json.dumps(game_attempt))

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Submission successful",
                "group_id": group_id
            })
        }
    except ValueError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": str(e)
            })
        }
    except Exception as e: 
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }  