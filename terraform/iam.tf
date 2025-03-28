resource "aws_iam_role" "lambda_role" {
  name = "photo-ranker-lambda-role-${terraform.workspace}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "s3" {
  name        = "photo-ranker-s3-policy-${terraform.workspace}"
  description = "Allows s3 session images bucket to be written to"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = [
          aws_s3_bucket.session_images.arn,
          "${aws_s3_bucket.session_images.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "session_images" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.s3.arn
}

resource "aws_iam_policy" "dynamodb" {
  name        = "photo-ranker-dynamodb-policy-${terraform.workspace}"
  description = "Allows photo-ranker lambda functions to access the dynamodb resource"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.sessions.arn
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "session_items" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamodb.arn
}

resource "aws_iam_policy" "rds" {
  name        = "photo-ranker-rds-policy-${terraform.workspace}"
  description = "Allows Lambda to access RDS for REST operations"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds-db:connect"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_rds_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.rds.arn
}

resource "aws_iam_policy" "logs" {
  name        = "photo-ranker-logs-${terraform.workspace}"
  description = "Allows basic logging"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "create_session_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.logs.arn
}