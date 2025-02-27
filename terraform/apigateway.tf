resource "aws_api_gateway_rest_api" "photo_ranker_api" {
  name        = "photo-ranker-api-${terraform.workspace}"
  description = "API for interfacing with photo ranker lambdas"
}

// Define API path
resource "aws_api_gateway_resource" "create_session_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "create-session"
}
resource "aws_api_gateway_resource" "update_session_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "update-session"
}
resource "aws_api_gateway_resource" "get_session_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "get-session"
}

// API Gateway method
resource "aws_api_gateway_method" "create_session_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.create_session_resource.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "update_session_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.update_session_resource.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "get_session_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.get_session_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

// API Gateway method response

variable "allowed_origins" {
  type    = list(string)
  default = ["https://pickpix.vercel.app"]
}

locals {
  final_allowed_origins = terraform.workspace == "dev" ? concat(var.allowed_origins, ["http://localhost:3000"]) : var.allowed_origins
}

resource "aws_api_gateway_method_response" "create_session_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.create_session_resource.id
  http_method = aws_api_gateway_method.create_session_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}

resource "aws_api_gateway_method_response" "update_session_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.update_session_resource.id
  http_method = aws_api_gateway_method.update_session_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}

resource "aws_api_gateway_method_response" "get_session_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.get_session_resource.id
  http_method = aws_api_gateway_method.get_session_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}



// Integrate API gateway
resource "aws_api_gateway_integration" "create_session_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.create_session_resource.id
  http_method             = aws_api_gateway_method.create_session_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_session.invoke_arn
}
resource "aws_api_gateway_integration" "update_session_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.update_session_resource.id
  http_method             = aws_api_gateway_method.update_session_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_session.invoke_arn
}

resource "aws_api_gateway_integration" "get_session_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.get_session_resource.id
  http_method             = aws_api_gateway_method.get_session_method.http_method
  integration_http_method = "GET"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_session.invoke_arn
}

// Integration responses
resource "aws_api_gateway_integration_response" "create_session_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.create_session_resource.id
  http_method = aws_api_gateway_method.create_session_method.http_method
  status_code = aws_api_gateway_method_response.create_session_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "\"${join(",", local.final_allowed_origins)}\"",
    "method.response.header.Access-Control-Allow-Methods" = "'POST'"
  }
}
resource "aws_api_gateway_integration_response" "update_session_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.update_session_resource.id
  http_method = aws_api_gateway_method.update_session_method.http_method
  status_code = aws_api_gateway_method_response.update_session_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "\"${join(",", local.final_allowed_origins)}\"",
    "method.response.header.Access-Control-Allow-Methods" = "'POST'"
  }
}
resource "aws_api_gateway_integration_response" "get_session_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.get_session_resource.id
  http_method = aws_api_gateway_method.get_session_method.http_method
  status_code = aws_api_gateway_method_response.get_session_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "\"${join(",", local.final_allowed_origins)}\"",
    "method.response.header.Access-Control-Allow-Methods" = "'GET'"
  }
}

# Deploy API Gateway
resource "aws_api_gateway_deployment" "photo_ranker_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.create_session_lambda_integration,
    aws_api_gateway_integration.get_session_lambda_integration,
    aws_api_gateway_integration.update_session_lambda_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id

  lifecycle {
    create_before_destroy = true
  }
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.photo_ranker_api.id
    ]))
  }
}

resource "aws_api_gateway_stage" "photo_ranker_api_stage" {
  deployment_id = aws_api_gateway_deployment.photo_ranker_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  stage_name    = "photo-ranker-api-${terraform.workspace}"
}


# Give lambda permissions to API gateway
resource "aws_lambda_permission" "api_gateway_invoke_create_session" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_session.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.photo_ranker_api.execution_arn}/*/*"
}
resource "aws_lambda_permission" "api_gateway_invoke_update_session" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_session.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.photo_ranker_api.execution_arn}/*/*"
}
resource "aws_lambda_permission" "api_gateway_invoke_get_session" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_session.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.photo_ranker_api.execution_arn}/*/*"
}