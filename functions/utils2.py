import boto3
import os

dynamodb_client = boto3.client('dynamodb')
DYNAMODB_TABLE = os.environ['IMAGES_DYNAMODB_TABLE']


def check_image_exists_in_db(pk_value):
    response = dynamodb_client.get_item(
        TableName=DYNAMODB_TABLE,
        Key={"tag": {"S": pk_value}}  
    )
    return "Item" in response

def validate_images(images):
    for image in images:
        tag = image.get('tag')
        start_index = image.get('start_index')
        end_index = image.get('end_index')

        if start_index < 0 or end_index > len(tag):
            raise ValueError(f"Invalid start_index or end_index for tag '{tag}'.")

        if start_index >= end_index:
            raise ValueError(f"start_index must be less than end_index for tag '{tag}'.")

        if not check_image_exists_in_db(tag):
            raise ValueError(f"Image with tag '{tag}' does not exist")