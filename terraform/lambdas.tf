resource "aws_lambda_function" "create_session" {
  function_name    = "photo-ranker-create-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src/create_session.create_session_handler"
  runtime          = "python3.9"
  timeout          = 5
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.session_images.bucket
      DB_HOST        = aws_db_instance.photo_ranking_db.address
      DB_NAME        = aws_db_instance.photo_ranking_db.db_name
      DB_USER        = aws_db_instance.photo_ranking_db.username
      DB_PASSWORD    = aws_db_instance.photo_ranking_db.password
    }
  }
}

resource "aws_lambda_function" "edit_session" {
  function_name    = "photo-ranker-edit-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src/edit_session.edit_session_handler"
  runtime          = "python3.9"
  timeout          = 5
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")

  environment {
    variables = {
      S3_BUCKET_NAME      = "${aws_s3_bucket.session_images.bucket}"
      DYNAMODB_TABLE_NAME = "${aws_dynamodb_table.sessions.name}"
      TERRAFORM_WORKSPACE = "${terraform.workspace}"
    }
  }
}

resource "aws_lambda_function" "get_session" {
  function_name    = "photo-ranker-get-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src/get_session.get_session_handler"
  runtime          = "python3.9"
  timeout          = 5
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")

  environment {
    variables = {
      S3_BUCKET_NAME      = "${aws_s3_bucket.session_images.bucket}"
      DYNAMODB_TABLE_NAME = "${aws_dynamodb_table.sessions.name}"
      TERRAFORM_WORKSPACE = "${terraform.workspace}"
    }
  }
}

resource "aws_lambda_function" "delete_session" {
  function_name    = "photo-ranker-delete-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src/delete_session.delete_session_handler"
  runtime          = "python3.9"
  timeout          = 5
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")

  environment {
    variables = {
      S3_BUCKET_NAME = "${aws_s3_bucket.session_images.bucket}"
      DB_HOST        = aws_db_instance.photo_ranking_db.address
      DB_NAME        = aws_db_instance.photo_ranking_db.db_name
      DB_USER        = aws_db_instance.photo_ranking_db.username
      DB_PASSWORD    = aws_db_instance.photo_ranking_db.password
    }
  }
}