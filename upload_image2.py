import io 
import base64
import cgi 
import json
import boto3 
import uuid


s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

S3_BUCKET = 'photowords'

def get_file_from_request_body(content_type: str, body: str):
    try:
        fp = io.BytesIO(base64.b64decode(body))

        environ = {"REQUEST_METHOD": "POST"}
        headers = {"content-type": content_type}

        fs = cgi.FieldStorage(fp=fp, environ=environ, headers=headers)
        return fs["file"]
    except Exception as error:
        print(f"Error decoding file content: {error}")
        return None


def lambda_handler(event, context):
    try:
        content_type = event['headers'].get('Content-Type')
        file_item = get_file_from_request_body(content_type, event['body'])
        if not file_item:
            return {"statusCode": 400, "body": json.dumps("No file foiund")}
        
        s3_key = f"client/{str(uuid.uuid4())}"
        s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=file_item,
                ContentType='image/jpeg'
            )
        s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image uploaded successfully!',
                's3Url': s3_url
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

    
    