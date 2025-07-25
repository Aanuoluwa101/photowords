# # make this into a script
# def fetch_all_groups():
#     """
#     Fetch the 'all_groups' item from DynamoDB.
#     If it doesn't exist, create it with an empty 'groups' list.
#     """
#     try:
#         response = dynamodb.get_item(
#             TableName=DYNAMODB_TABLE,
#             Key={'id': {'S': 'all_groups'}}
#         )
#         if 'Item' in response:
#             return response['Item']
#         else:
#             all_groups_item = {
#                 'id': {'S': 'all_groups'},
#                 'groups': {'L': []}  
#             }
#             dynamodb.put_item(
#                 TableName=DYNAMODB_TABLE,
#                 Item=all_groups_item
#             )
#             return all_groups_item
#     except Exception as e:
#         raise Exception(f"Error fetching or creating 'all_groups': {str(e)}")