import json
import boto3
import random
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['GROUPS_DYNAMODB_TABLE'])

def fetch_all_groups_ids():
    try:
        response = table.get_item(
            Key={'id': 'all_groups'}
        )
        if 'Item' in response:
            group_ids = response['Item']['groups']
            return group_ids
        else:
            return []
    except Exception as e:
        raise Exception(f"Error fetching 'all_groups': {str(e)}")

def fetch_group_by_id(group_id):
    try:
        response = table.get_item(
            Key={'id': group_id}
        )
        if 'Item' in response:
            return response['Item']
        else:
            return None
    except Exception as e:
        raise Exception(f"Error fetching group by ID: {str(e)}")

def format_group(group):
    formatted_group = {
        'id': group['id'],
        'answer': group['answer'],
        'difficulty': int(group['difficulty']),
        'hint': group['hint'],
        'created_at': group['created_at'],
        'images': [
            {
                'tag': image['tag'],
                'start_index': int(image['start_index']),
                'end_index': int(image['end_index']),
                'position': int(image['position'])
            } for image in group['images']
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
            count = int(count)
            selected_group_ids = group_ids
            try:
                selected_group_ids = random.sample(group_ids, count)
            except ValueError:
                pass
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'groups': selected_group_ids
                })
            }
        else:
            if not group_ids:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        'error': 'No groups found.'
                    })
                }
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'groups': group_ids
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
