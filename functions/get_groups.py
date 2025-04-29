import json
import boto3
import random
import os

dynamodb = boto3.client('dynamodb')
DYNAMODB_TABLE = os.environ['GROUPS_DYNAMODB_TABLE']

def fetch_all_groups_ids():
    """
    Fetch the 'all_groups' item from DynamoDB.
    """
    try:
        response = dynamodb.get_item(
            TableName=DYNAMODB_TABLE,
            Key={'id': {'S': 'all_groups'}}
        )
        if 'Item' in response:
            group_ids = response['Item']['groups']['L']
            return [{'id': {'S': group_id}} for group_id in group_ids]
        else:
            return []
    except Exception as e:
        raise Exception(f"Error fetching 'all_groups': {str(e)}")

def fetch_group_by_id(group_id):
    """
    Fetch a group by its ID from DynamoDB.
    """
    try:
        response = dynamodb.get_item(
            TableName=DYNAMODB_TABLE,
            Key={'id': {'S': group_id}}
        )
        if 'Item' in response:
            return response['Item']
        else:
            return None
    except Exception as e:
        raise Exception(f"Error fetching group by ID: {str(e)}")
    
def fetch_groups_by_ids(group_ids):
    """
    Fetch multiple groups by their IDs using batch_get_item.
    """
    try:
        # Fetch the groups
        response = dynamodb.batch_get_item(
            RequestItems={
                DYNAMODB_TABLE: {
                    'Keys': group_ids
                }
            }
        )

        # Extract the groups from the response
        groups = response.get('Responses', {}).get(DYNAMODB_TABLE, [])
        return groups
    except Exception as e:
        raise Exception(f"Error fetching groups by ids: {str(e)}")



def fetch_groups_by_count(group_ids, count):
    """
    Fetch a specified number of groups from the list of group IDs.
    """
    if not group_ids:
        return []

    # Select 'count' number of group IDs (or all if count > number of groups)
    selected_group_ids = group_ids
    try:
        selected_group_ids = random.sample(group_ids, count)
    except ValueError:
        pass

    return fetch_groups_by_ids(selected_group_ids)

def format_group(group):
    """
    Convert a DynamoDB group item into a standard Python dictionary.
    """
    formatted_group = {
        'id': group['id']['S'],
        'answer': group['answer']['S'],
        'difficulty': int(group['difficulty']['N']),
        'hint': group['hint']['S'],
        'created_at': group['created_at']['S'],
        'images': [
            {
                'tag': image['M']['tag']['S'],
                'url': image['M']['url']['S'],
                'start_index': int(image['M']['start_index']['N']),
                'end_index': int(image['M']['end_index']['N'])
            } for image in group['images']['L']
        ]
    }
    return formatted_group

def lambda_handler(event, context):
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters', {})
        group_id = count = None 
        if query_params:
            group_id = query_params.get('id')
            count = query_params.get('count')

        # Fetch the list of group IDs from 'all_groups'
        group_ids = fetch_all_groups_ids()
        
        # Fetch groups based on query parameters
        if group_id:
            # Fetch the group with the specified ID
            group = fetch_group_by_id(group_id)
            if not group:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        'error': f'Group with ID {group_id} not found.'
                    })
                }
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'group': format_group(group)
                })
            }
        elif count:
            # Fetch the specified number of groups
            count = int(count)
            groups = fetch_groups_by_count(group_ids, count)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'groups': [format_group(group) for group in groups]
                })
            }
        else:
            # Fetch all groups
            groups = fetch_groups_by_ids(group_ids)
            if not group:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        'error': 'No groups found.'
                    })
                }
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'group': format_group(group)
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }