# photowords-elasticache-allow-all 
photowords-elasticache-allow-all = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "elasticache:Connect"
            ],
            "Resource": [
                "arn:aws:elasticache:eu-west-2:182399698888:replicationgroup:photowords-redis-cluster",
                "arn:aws:elasticache:eu-west-2:182399698888:user:photowords-redis"
            ]
        }
    ]
}

# parameter-read-access
parameter-read-access = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "ssm:GetParameter",
            "Resource": "arn:aws:ssm:*:182399698888:parameter/*"
        }
    ]
}


# photowords-lambda-policy. I should probably just call this photowords-lambda-dynamo-access
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGetItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:eu-west-2:182399698888:table/photowords_users",
                "arn:aws:dynamodb:eu-west-2:182399698888:table/photowords_images",
                "arn:aws:dynamodb:eu-west-2:182399698888:table/photowords_image_groups",
                "arn:aws:dynamodb:eu-west-2:182399698888:table/photowords_game_attempts"
            ]
        },
        # this next part is quite unneccary. It's already in AWSLambdaBasicExecutionRole
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:eu-west-2:182399698888:*"
        },
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "*"
        }
    ]
}