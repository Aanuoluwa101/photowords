import json
import boto3
import random
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

def cache_group(group):
    group_id = group['id']
    redis_client.set(f"group:{group_id}", json.dumps(group))
    redis_client.sadd("all_groups", group_id)

def get_cached_group(group_id):
    group_data = redis_client.get(f"group:{group_id}")
    if group_data:
        return json.loads(group_data)
    return None

def fetch_all_groups_ids():
    try:
        group_ids = redis_client.smembers("all_groups")
        if group_ids:
            return list(group_ids)

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
                all_groups.append(item['id'])
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None

        return all_groups

    except Exception as e:
        raise Exception(f"Error fetching all groups: {str(e)}")

def fetch_group_by_id(group_id):
    try:
        group = get_cached_group(group_id)
        if group:
            return group
        
        response = table.get_item(Key={'id': group_id})
        if 'Item' in response:
            group = response['Item']
            cache_group(group)
            return group
        return None
    except Exception as e:
        raise Exception(f"Error fetching group by ID: {str(e)}")


def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters', {})
        group_id = count = None
        if query_params:
            group_id = query_params.get('id')
            count = query_params.get('count')

        all_group_ids = fetch_all_groups_ids()

        if group_id:
            group = fetch_group_by_id(group_id)
            if not group:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f'Group with ID {group_id} not found.'})
                }
            return {
                'statusCode': 200,
                'body': json.dumps(group)
            }

        elif count:
            count = int(count)
            try:
                selected_ids = random.sample(all_group_ids, count)
            except ValueError:
                selected_ids = all_group_ids  # fallback to all
            groups = [fetch_group_by_id(gid) for gid in selected_ids]
            return {
                'statusCode': 200,
                'body': json.dumps(groups)
            }

        else:
            if not all_group_ids:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'No groups found.'})
                }
            groups = [fetch_group_by_id(gid) for gid in all_group_ids]
            return {
                'statusCode': 200,
                'body': json.dumps(groups)
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
