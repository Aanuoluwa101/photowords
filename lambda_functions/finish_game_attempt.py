"""
his function marks a game attempt as finished. 
It takes the attempt ID from the request, validates and processes
the submitted answers, updates the attempt's status and details in DynamoDB,
deletes the attempt from Redis cache, and returns a confirmation response or 
an error if something goes wrong."""


from redis_client import ElastiCacheIAMProvider
import json
from datetime import datetime, timezone
import os
import boto3
import redis


# Environment setup
ATTEMPTS_DYNAMODB_TABLE = os.environ['ATTEMPTS_DYNAMODB_TABLE']
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_CACHE_NAME = os.environ.get("REDIS_CACHE_NAME")

# DynamoDB resource
dynamodb = boto3.resource('dynamodb')
attempts_table = dynamodb.Table(ATTEMPTS_DYNAMODB_TABLE)

# Redis setup
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

def lambda_handler(event, context):
    try:
        # Extract attempt ID from path
        game_attempt_id = event["pathParameters"]["game_attempt_id"]

        body = json.loads(event['body'])
        time_taken = body["time_taken"]
        time_requested = body.get("time_requested")
        answers = body["answers"]

        redis_key = f"attempt:{game_attempt_id}"
        game_attempt_json = redis_client.get(redis_key)
        if not game_attempt_json:
            return {
                    'statusCode': 404,
                    'body': json.dumps({'error': "Game attempt not found"})
                }

        game_attempt = json.loads(game_attempt_json)
        question_ids = [q["id"] for q in game_attempt.get("questions", [])]

        questions_answered_count = 0
        for answer in answers:
            if answer["question_id"] not in question_ids:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f"Question {answer['question_id']} not found in game attempt"})
                }
            questions_answered_count += 1

        # Update the attempt in DynamoDB
        attempts_table.update_item(
            Key={'id': game_attempt_id},
            UpdateExpression="""
                SET finished_at = :finished_at,
                    answers = :answers,
                    questions_answered_count = :qac,
                    status = :status,
                    time_taken = :time_taken,
                    time_requested = :time_requested
            """,
            ExpressionAttributeValues={
                ':finished_at': datetime.now(timezone.utc).isoformat(),
                ':answers': answers,
                ':qac': questions_answered_count,
                ':status': 'COMPLETED',
                ':time_taken': time_taken,
                ':time_requested': time_requested
            }
        )

        redis_client.delete(redis_key)

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Game finished",
                "game_attempt": game_attempt_id
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
