resource "aws_lambda_function" "create_session" {
  function_name    = "photo-ranker-create-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "create_session.create_session_handler"
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
      API_AUDIENCE = var.api_audience
      AUTH0_DOMAIN = var.auth0_domain
    }
  }
}

resource "aws_lambda_function" "edit_session" {
  function_name    = "photo-ranker-edit-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "edit_session.edit_session_handler"
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
      API_AUDIENCE = var.api_audience
      AUTH0_DOMAIN = var.auth0_domain
    }
  }
}

resource "aws_lambda_function" "get_session" {
  function_name    = "photo-ranker-get-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "get_session.get_session_handler"
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
      API_AUDIENCE = var.api_audience
      AUTH0_DOMAIN = var.auth0_domain
    }
  }
}

resource "aws_lambda_function" "delete_session" {
  function_name    = "photo-ranker-delete-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "delete_session.delete_session_handler"
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
      API_AUDIENCE = var.api_audience
      AUTH0_DOMAIN = var.auth0_domain
    }
  }
}

resource "aws_lambda_function" "register_user" {
  function_name    = "photo-ranker-register-user-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "register_user.register_user_handler"
  runtime          = "python3.9"
  timeout          = 5
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")

  environment {
    variables = {
      DB_HOST      = aws_db_instance.photo_ranking_db.address
      DB_NAME      = aws_db_instance.photo_ranking_db.db_name
      DB_USER      = aws_db_instance.photo_ranking_db.username
      DB_PASSWORD  = aws_db_instance.photo_ranking_db.password
      API_AUDIENCE = var.api_audience
      AUTH0_DOMAIN = var.auth0_domain
    }
  }
}

resource "aws_lambda_function" "add_reaction" {
  function_name    = "photo-ranker-add-reaction-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src/add_reaction.add_reaction_handler"
  runtime          = "python3.9"
  timeout          = 5
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")

  environment {
    variables = {
      DB_HOST     = aws_db_instance.photo_ranking_db.address
      DB_NAME     = aws_db_instance.photo_ranking_db.db_name
      DB_USER     = aws_db_instance.photo_ranking_db.username
      DB_PASSWORD = aws_db_instance.photo_ranking_db.password
      API_AUDIENCE = var.api_audience
      AUTH0_DOMAIN = var.auth0_domain
    }
  }
}

resource "aws_lambda_function" "remove_reaction" {
  function_name    = "photo-ranker-remove-reaction-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src/remove_reaction.remove_reaction_handler"
  runtime          = "python3.9"
  timeout          = 5
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")

  environment {
    variables = {
      DB_HOST     = aws_db_instance.photo_ranking_db.address
      DB_NAME     = aws_db_instance.photo_ranking_db.db_name
      DB_USER     = aws_db_instance.photo_ranking_db.username
      DB_PASSWORD = aws_db_instance.photo_ranking_db.password
      API_AUDIENCE = var.api_audience
      AUTH0_DOMAIN = var.auth0_domain
    }
  }
}