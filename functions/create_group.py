import json
import boto3
import uuid
from datetime import datetime
import os
from update_all_groups import add_group_to_all_groups
from utils import validate_images

dynamodb = boto3.client('dynamodb')
DYNAMODB_TABLE = os.environ['GROUPS_DYNAMODB_TABLE']

s3_client = boto3.client('s3')
S3_BUCKET = os.environ['S3_BUCKET']
        
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        hint = body.get('hint')
        images = body.get('images')

        validate_images(images)
        group_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        item = {
            'id': {'S': group_id},
            'answer': {'S': answer},
            'difficulty': {'N': str(difficulty)},
            'hint': {'S': hint},
            'images': {'L': [
                {
                    'M': {
                        'tag': {'S': image['tag']},
                        'url': {'S': image['url']},
                        'start_index': {'N': str(image['start_index'])},
                        'end_index': {'N': str(image['end_index'])},
                        'part_index': {'N': str(image['part_index'])}
                    }
                } for image in images
            ]},
            'created_at': {'S': created_at}
        }

        dynamodb.put_item(
            TableName=DYNAMODB_TABLE,
            Item=item
        )

        add_group_to_all_groups(group_id)

        # save to storage 
        data = body.copy() 
        data['id'] = group_id
        data['created_at'] = created_at
        object_key = f'groups/{group_id}'
        s3_client.put_object(
            Bucket=S3_BUCKET, 
            Key=object_key, 
            Body=json.dumps(data),
            ContentType="application/json"
        )
        
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