import json
import boto3
import os

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

def delete_group_by_id(group_id):
    """
    Delete a group by its ID from DynamoDB.
    """
    try:
        table.delete_item(Key={'id': group_id})
    except Exception as e:
        raise Exception(f"Error deleting group: {str(e)}")

def remove_group_from_all_groups(group_id):
    """
    Remove a group ID from the 'groups' list in the 'all_groups' item.
    """
    try:
        # Get current 'groups' list
        response = table.get_item(Key={'id': 'all_groups'})
        
        if 'Item' not in response or 'groups' not in response['Item']:
            raise Exception("No groups found in 'all_groups'.")
        
        groups = response['Item']['groups']

        # Find index of the group ID to remove
        index_to_remove = next(
            (i for i, v in enumerate(groups) if v == group_id), None
        )

        if index_to_remove is None:
            raise ValueError(f"Group not found.")

        # Remove the group ID using list_remove expression
        table.update_item(
            Key={'id': 'all_groups'},
            UpdateExpression=f"REMOVE #groups[{index_to_remove}]",
            ExpressionAttributeNames={'#groups': 'groups'}
        )
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Error removing group from 'all_groups': {str(e)}")

def lambda_handler(event, context):
    try:
        group_id = event.get("queryStringParameters", {}).get("id")
        if not group_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Group ID is required.'})
            }

        # Delete the group from DynamoDB
        delete_group_by_id(group_id)

        # Remove the group ID from the 'all_groups' list
        remove_group_from_all_groups(group_id)

        return {
            'statusCode': 204,
            'body': json.dumps({
                'message': f'Group {group_id} deleted successfully!'
            })
        }
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
