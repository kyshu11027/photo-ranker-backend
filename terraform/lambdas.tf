resource "aws_lambda_function" "create_session" {
  function_name    = "photo-ranker-create-new-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.create_new_session_handler"
  runtime          = "python3.9"
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")
}

resource "aws_lambda_function" "update_session" {
  function_name    = "photo-ranker-update-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src/app.update_session_handler"
  runtime          = "python3.9"
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")
}

resource "aws_lambda_function" "get_session" {
  function_name    = "photo-ranker-get-session-${terraform.workspace}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src/app.update_session_handler"
  runtime          = "python3.9"
  filename         = "src.zip"
  source_code_hash = filebase64sha256("src.zip")
}