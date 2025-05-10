import json
import redis
import os
from redis_client import ElastiCacheIAMProvider

# Redis Setup
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_CACHE_NAME = os.environ.get("REDIS_CACHE_NAME")
SUPER_ADMIN_USERNAME = os.environ.get("SUPER_ADMIN_USERNAME")

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
        query = event.get('queryStringParameters') or {}
        target = query.get('target')
        id = query.get('id')

        username = event['requestContext']['authorizer']['claims']["cognito:username"]
        if username != SUPER_ADMIN_USERNAME:
            return {
                "statusCode": 403,
                "body": json.dumps({"error": "You can not access this resource"})
            }

        if not target:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Query parameter 'target' is required."})
            }

        results = {}

        if target == "all":
            for key in redis_client.scan_iter("*"):
                if key.startswith("all"):
                    value = list(redis_client.smembers(key))
                else:
                    value = json.loads(redis_client.get(key))
                results[key] = value

        elif target == "group":
            if id:
                key = f"{target}:{id}"
                value = redis_client.get(key)
                if value is None:
                    return {
                        "statusCode": 404,
                        "body": json.dumps({"error": f"{target} with id {id} not found."})
                    }
                results[key] = json.loads(value)
            else:
                for key in redis_client.scan_iter(f"{target}:*"):
                    results[key] = json.loads(redis_client.get(key))

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown target: {target}"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(results)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
