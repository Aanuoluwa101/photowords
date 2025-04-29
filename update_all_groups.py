import boto3
import os 

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')
DYNAMODB_TABLE = os.environ['GROUPS_DYNAMODB_TABLE']


# make this into a script
def fetch_all_groups():
    """
    Fetch the 'all_groups' item from DynamoDB.
    If it doesn't exist, create it with an empty 'groups' list.
    """
    try:
        response = dynamodb.get_item(
            TableName=DYNAMODB_TABLE,
            Key={'id': {'S': 'all_groups'}}
        )
        if 'Item' in response:
            return response['Item']
        else:
            all_groups_item = {
                'id': {'S': 'all_groups'},
                'groups': {'L': []}  
            }
            dynamodb.put_item(
                TableName=DYNAMODB_TABLE,
                Item=all_groups_item
            )
            return all_groups_item
    except Exception as e:
        raise Exception(f"Error fetching or creating 'all_groups': {str(e)}")

def add_group_to_all_groups(group_id):
    """
    Add a new group ID to the 'groups' list in the 'all_groups' item.
    """
    try:
        dynamodb.update_item(
            TableName=DYNAMODB_TABLE,
            Key={'id': {'S': 'all_groups'}},
            UpdateExpression="SET #groups = list_append(#groups, :new_group_id)",
            ExpressionAttributeNames={
                '#groups': 'groups'
            },
            ExpressionAttributeValues={
                ':new_group_id': {'L': [{'S': group_id}]}
            }
        )
    except Exception as e:
        raise Exception(f"Error updating 'all_groups': {str(e)}")

