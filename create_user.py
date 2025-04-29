import boto3 
from dotenv import load_dotenv 
import os
from botocore.exceptions import ClientError


          
# import botocore.exceptions

# for key, value in sorted(botocore.exceptions.__dict__.items()):
#     if isinstance(value, type):
#         print(key)


load_dotenv()

client = boto3.client(
                'elasticache',
                aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
                region_name='eu-west-2'
            )

def create_elasticache_iam_user(user_id, username):
    try:
        # create user
        response = client.create_user(
            UserId=user_id,
            UserName=username,
            Engine="redis",
            AccessString="on ~* +@all",
            AuthenticationMode={
                "Type": "iam"
            }
        )
        
        return response['Status']
    except ClientError as e:
        print(f"Error creating elasticache iam user: {e}")

def create_elasticache_default_user():
    try:
        # create default user
        response = client.create_user_group(
            UserId="default-user-disabled",
            UserName="default",
            Engine="redis",
            AccessString="off +get ~keys*",
            AuthenticationMode={
                "Type": "no-password-required"
            }
        )
        
        return response['Status']
    except ClientError as e:
        print(f"Error creating elasticache default user: {e}")


def create_user_group():
    try:
        # create default user
        response = client.create_user_group(
            UserGroupId='photowords-redis-user-group',
            Engine='redis',
            UserIds=[
                'photowords-redis',
                'default-user-disabled'
            ]
        )
        
        return response['UserGroupId']   
    except ClientError as e:
        print(f"Error creating user group: {e}")  


def attach_user_group_to_replication_group():
    try:
        response = client.modify_replication_group(
            ReplicationGroupId='photowords-redis-cluster',
            UserGroupIdsToAdd=[
                'photowords-redis-user-group',
            ]
        )
        
        return response
    except ClientError as e:
        print(f"Error attaching user group to replication group: {e}")  


if __name__ == "__main__":
    # print(create_elasticache_iam_user("photowords-redis", "photowords-redis"))
    # print(create_elasticache_default_user())
    # print(create_user_group())
    # print(attach_user_group_to_replication_group())
    print(client.describe_replication_groups(ReplicationGroupId="photowords-redis-cluster"))