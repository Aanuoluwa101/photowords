import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    try:
        response = table.get_item(
            Key={'tag': 'all_images'}
        )
        if 'Item' in response:
            images = response['Item']['images']
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'images': [image for image in images]
                })
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'No images found.'
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
