import json
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo
import os

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

S3_BUCKET = os.environ['S3_BUCKET']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
CLOUDFRONT_URL_PREFIX = os.environ.get('CLOUDFRONT_URL_PREFIX')

def check_image_exists_in_db(tag):
    """Check if an image with the given tag exists in DynamoDB"""
    response = dynamodb_client.get_item(
        TableName=DYNAMODB_TABLE,
        Key={"tag": {"S": tag}}
    )
    return "Item" in response


def add_image_to_all_images(image_tag):
    try:
        dynamodb_client.update_item(
            TableName=DYNAMODB_TABLE,
            Key={'tag': {'S': 'all_images'}},
            UpdateExpression="SET #images = list_append(#images, :new_image_tag)",
            ExpressionAttributeNames={
                '#images': 'images'
            },
            ExpressionAttributeValues={
                ':new_image_tag': {'L': [{'S': image_tag}]}
            }
        )
    except Exception as e:
        raise Exception(f"Error updating 'all_images': {str(e)}")


def lambda_handler(event, context):
    """Register a new image in the DynamoDB images table.
        This function is called by s3 after we use a presigned url to upload an image to the images folder
        image = {
            "tag": "string", 
            "cloudfront_url": "string",
            "image_type": "string",
            "s3_url": "string",
            "uploaded_at": "string
          }
    """
    try:
        for record in event['Records']:
            s3_bucket = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']

            # Ensure it's inside the 'images/' folder
            if not object_key.startswith("images/"):
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': f'An image with the tag "{tag}" not in images folder.'
                    })
                }

            # Extract the tag from filename (e.g., "images/tag123.png" -> "tag123.png")
            tag = object_key.split("/")[-1].split(".")[0]

            # Check if image is already registered
            if check_image_exists_in_db(tag):
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': f'An image with the tag "{tag}" already registered.'
                    })
                }

            # Construct S3 and CloudFront URLs
            s3_url = f"https://{s3_bucket}.s3.amazonaws.com/{object_key}"
            cloudfront_url = f"{CLOUDFRONT_URL_PREFIX}/{object_key}"
            uploaded_at = datetime.now(tz=ZoneInfo("UTC")).isoformat()

            # Save image details in DynamoDB
            dynamodb_client.put_item(
                TableName=DYNAMODB_TABLE,
                Item={
                    'tag': {"S": tag},
                    'uploaded_at': {"S": uploaded_at}
                }
            )
        
            # Add image to 'all_images' list
            add_image_to_all_images(tag)
            print(f"Image '{tag}' successfully registered in DynamoDB.")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processing complete.'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
