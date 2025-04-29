import boto3 
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os


load_dotenv() 

client = boto3.client(
                'iam',
                aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
                region_name='eu-west-2'
            )

def create_policy():
    try: 
        response = client.create_policy(
            PolicyName='photowords-elasticache-allow-all',
            PolicyDocument='policy.json'
        )
        return response['Policy']['Arn']
    except ClientError as e:
        print(f"Error creating policy: {e}")
        raise e

if __name__ == "__main__":
    print(create_policy())