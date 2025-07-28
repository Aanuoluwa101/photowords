"""
This function allows a super admin to clear cached data 
in Redis. Depending on the request, it can delete all cache
 entries, all entries of a specific type (like "group" or "image"),
 or a single entry by ID. Access is restricted to the super
 admin, and responses are returned in JSON format.
"""


import json
import os
import redis
from redis_client import ElastiCacheIAMProvider

# Redis Config
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_CACHE_NAME = os.environ.get("REDIS_CACHE_NAME")
SUPER_ADMIN_USERNAME = os.environ.get("SUPER_ADMIN_USERNAME")


# Credentials for IAM-authenticated ElastiCache
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

def delete_keys_with_prefix(prefix):
    deleted_count = 0
    for key in redis_client.scan_iter(match=f"{prefix}:*"):
        redis_client.delete(key)
        deleted_count += 1
    return deleted_count

def lambda_handler(event, context):
    try:
        body = event.get('body') or "{}"
        body = json.loads(body)
        target = body.get("target")
        item_id = body.get("id")

        username = event['requestContext']['authorizer']['claims']["cognito:username"]
        if username != SUPER_ADMIN_USERNAME:
            return {
                "statusCode": 403,
                "body": json.dumps({"error": "You can not access this resource"})
            }

        if not target:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'target' in request body"})
            }

        if target == "all":
            deleted = 0
            for key in redis_client.scan_iter(match="*"):
                redis_client.delete(key)
                deleted += 1
            return {
                "statusCode": 200,
                "body": json.dumps({"message": f"Deleted all keys ({deleted} total)."})
            }

        if target not in ["group", "image"]:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid 'target'. Must be 'group', 'image', or 'all'."})
            }

        if item_id:
            key = f"{target}:{item_id}"
            deleted = redis_client.delete(key)
            if deleted:
                return {
                    "statusCode": 200,
                    "body": json.dumps({"message": f"Deleted {key} from cache."})
                }
            else:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": f"{key} not found in cache."})
                }

        # No item_id provided – delete all keys under target
        deleted_count = delete_keys_with_prefix(target)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Deleted {deleted_count} {target} keys from cache."})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
