import json
import boto3
import uuid
from datetime import datetime
import os
from update_all_groups import add_group_to_all_groups
from utils2 import validate_images

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

S3_BUCKET = os.environ['S3_BUCKET']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']



        
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        hint = body.get('hint')
        images = body.get('images')

        validate_images(images)
        group_id = str(uuid.uuid4())

        item = {
            'id': {'S': group_id},
            'answer': {'S': answer},
            'difficulty': {'N': str(difficulty)},
            'hint': {'S': hint},
            'images': {'L': [
                {
                    'M': {
                        'tag': {'S': image['tag']},
                        'start_index': {'N': str(image['start_index'])},
                        'end_index': {'N': str(image['end_index'])}
                    }
                } for image in images
            ]},
            'created_at': {'S': datetime.utcnow().isoformat()}
        }

        dynamodb.put_item(
            TableName=DYNAMODB_TABLE,
            Item=item
        )

        add_group_to_all_groups(group_id)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Group saved successfully!',
                'data': {
                    'id': group_id,
                    'answer': answer,
                    'difficulty': difficulty,
                    'hint': hint,
                    'images': images
                }
            })
        }

    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(e)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }