import boto3 

dbb = boto3.resource(
    "dynamodb",
    endpoint_url='http://localhost:8181',
    region_name="ajata",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy"
)

dbb.create_table(
    TableName='Users',
    AttributeDefinitions=[
        {
            'AttributeName': 'username',
            'AttributeType': 'S'  # Partition Key (Primary Key)
        },
        {
            'AttributeName': 'highest_score',
            'AttributeType': 'N'  # Sort Key
        }
    ],
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'  # Partition Key
        },
        {
            'AttributeName': 'highest_score',
            'KeyType': 'RANGE'  # Sort Key
        }
    ], 
    ProvisionedThroughput={  # Use capital 'P' to match Boto3 requirements
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

print("Users table created successfully!")


table = dbb.Table('Users')
input = {'username': 'aea', 'password': "1234", 'highest_score': 0}

table.put_item(Item=input)
print("Item put into table")

scan_response = table.scan(TableName='Users')
for item in scan_response['Items']:
    print(item)