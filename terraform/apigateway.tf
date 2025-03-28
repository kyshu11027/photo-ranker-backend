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
resource "aws_api_gateway_resource" "edit_session_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "edit-session"
}
resource "aws_api_gateway_resource" "get_session_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "get-session"
}
resource "aws_api_gateway_resource" "delete_session_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "delete-session"
}
resource "aws_api_gateway_resource" "register_user_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "register-user"
}
resource "aws_api_gateway_resource" "add_reaction_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "add-reaction"
}
resource "aws_api_gateway_resource" "remove_reaction_resource" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  parent_id   = aws_api_gateway_rest_api.photo_ranker_api.root_resource_id
  path_part   = "remove-reaction"
}

locals {
  allowed_origins = terraform.workspace == "dev" ? "https://pickpix.vercel.app,http://localhost:3000" : "https://pickpix.vercel.app"
  allowed_headers = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
}

// Regular Methods
resource "aws_api_gateway_method" "create_session_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.create_session_resource.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "edit_session_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.edit_session_resource.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "get_session_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.get_session_resource.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "delete_session_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.delete_session_resource.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "register_user_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.register_user_resource.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "add_reaction_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.add_reaction_resource.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "remove_reaction_method" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.remove_reaction_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

// CORS OPTIONS methods
resource "aws_api_gateway_method" "create_session_options" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.create_session_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "edit_session_options" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.edit_session_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "get_session_options" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.get_session_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "delete_session_options" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.delete_session_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "register_user_options" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.register_user_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "add_reaction_options" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.add_reaction_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "remove_reaction_options" {
  rest_api_id   = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id   = aws_api_gateway_resource.remove_reaction_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

// Regular Method Responses
resource "aws_api_gateway_method_response" "create_session_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.create_session_resource.id
  http_method = aws_api_gateway_method.create_session_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "edit_session_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.edit_session_resource.id
  http_method = aws_api_gateway_method.edit_session_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "get_session_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.get_session_resource.id
  http_method = aws_api_gateway_method.get_session_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "delete_session_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.delete_session_resource.id
  http_method = aws_api_gateway_method.delete_session_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "register_user_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.register_user_resource.id
  http_method = aws_api_gateway_method.register_user_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "add_reaction_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.add_reaction_resource.id
  http_method = aws_api_gateway_method.add_reaction_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "remove_reaction_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.remove_reaction_resource.id
  http_method = aws_api_gateway_method.remove_reaction_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}

// OPTIONS Method Responses
resource "aws_api_gateway_method_response" "create_session_options_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.create_session_resource.id
  http_method = aws_api_gateway_method.create_session_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "edit_session_options_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.edit_session_resource.id
  http_method = aws_api_gateway_method.edit_session_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }

}
resource "aws_api_gateway_method_response" "get_session_options_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.get_session_resource.id
  http_method = aws_api_gateway_method.get_session_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "delete_session_options_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.delete_session_resource.id
  http_method = aws_api_gateway_method.delete_session_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "register_user_options_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.register_user_resource.id
  http_method = aws_api_gateway_method.register_user_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "add_reaction_options_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.add_reaction_resource.id
  http_method = aws_api_gateway_method.add_reaction_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}
resource "aws_api_gateway_method_response" "remove_reaction_options_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.remove_reaction_resource.id
  http_method = aws_api_gateway_method.remove_reaction_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}

// Regular Lambda Integrations
resource "aws_api_gateway_integration" "create_session_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.create_session_resource.id
  http_method             = aws_api_gateway_method.create_session_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_session.invoke_arn
}
resource "aws_api_gateway_integration" "edit_session_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.edit_session_resource.id
  http_method             = aws_api_gateway_method.edit_session_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.edit_session.invoke_arn
}
resource "aws_api_gateway_integration" "get_session_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.get_session_resource.id
  http_method             = aws_api_gateway_method.get_session_method.http_method
  integration_http_method = "POST" // Lambda always needs POST for invocation
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_session.invoke_arn
}
resource "aws_api_gateway_integration" "delete_session_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.delete_session_resource.id
  http_method             = aws_api_gateway_method.delete_session_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.delete_session.invoke_arn
}
resource "aws_api_gateway_integration" "register_user_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.register_user_resource.id
  http_method             = aws_api_gateway_method.register_user_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.register_user.invoke_arn
}
resource "aws_api_gateway_integration" "add_reaction_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.add_reaction_resource.id
  http_method             = aws_api_gateway_method.add_reaction_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.add_reaction.invoke_arn
}

resource "aws_api_gateway_integration" "remove_reaction_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id             = aws_api_gateway_resource.remove_reaction_resource.id
  http_method             = aws_api_gateway_method.remove_reaction_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.remove_reaction.invoke_arn
}

// OPTIONS Mock Integrations
resource "aws_api_gateway_integration" "create_session_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.create_session_resource.id
  http_method = aws_api_gateway_method.create_session_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_integration" "edit_session_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.edit_session_resource.id
  http_method = aws_api_gateway_method.edit_session_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_integration" "get_session_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.get_session_resource.id
  http_method = aws_api_gateway_method.get_session_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_integration" "delete_session_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.delete_session_resource.id
  http_method = aws_api_gateway_method.delete_session_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_integration" "register_user_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.register_user_resource.id
  http_method = aws_api_gateway_method.register_user_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_integration" "add_reaction_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.add_reaction_resource.id
  http_method = aws_api_gateway_method.add_reaction_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_integration" "remove_reaction_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.remove_reaction_resource.id
  http_method = aws_api_gateway_method.remove_reaction_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}

// Integration responses for OPTIONS methods
resource "aws_api_gateway_integration_response" "create_session_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.create_session_resource.id
  http_method = aws_api_gateway_method.create_session_options.http_method
  status_code = aws_api_gateway_method_response.create_session_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = "'${local.allowed_origins}'",
    "method.response.header.Access-Control-Allow-Methods"     = "'GET,OPTIONS,POST,PUT,DELETE'",
    "method.response.header.Access-Control-Allow-Headers"     = "'${local.allowed_headers}'",
    "method.response.header.Access-Control-Allow-Credentials" = "'true'"
  }
}
resource "aws_api_gateway_integration_response" "edit_session_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.edit_session_resource.id
  http_method = aws_api_gateway_method.edit_session_options.http_method
  status_code = aws_api_gateway_method_response.edit_session_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = "'${local.allowed_origins}'",
    "method.response.header.Access-Control-Allow-Methods"     = "'GET,OPTIONS,POST,PUT,DELETE'",
    "method.response.header.Access-Control-Allow-Headers"     = "'${local.allowed_headers}'",
    "method.response.header.Access-Control-Allow-Credentials" = "'true'"
  }
}
resource "aws_api_gateway_integration_response" "get_session_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.get_session_resource.id
  http_method = aws_api_gateway_method.get_session_options.http_method
  status_code = aws_api_gateway_method_response.get_session_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = "'${local.allowed_origins}'",
    "method.response.header.Access-Control-Allow-Methods"     = "'GET,OPTIONS,POST,PUT,DELETE'",
    "method.response.header.Access-Control-Allow-Headers"     = "'${local.allowed_headers}'",
    "method.response.header.Access-Control-Allow-Credentials" = "'true'"
  }
}
resource "aws_api_gateway_integration_response" "delete_session_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.delete_session_resource.id
  http_method = aws_api_gateway_method.delete_session_options.http_method
  status_code = aws_api_gateway_method_response.delete_session_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = "'${local.allowed_origins}'",
    "method.response.header.Access-Control-Allow-Methods"     = "'GET,OPTIONS,POST,PUT,DELETE'",
    "method.response.header.Access-Control-Allow-Headers"     = "'${local.allowed_headers}'",
    "method.response.header.Access-Control-Allow-Credentials" = "'true'"
  }
}
resource "aws_api_gateway_integration_response" "register_user_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.register_user_resource.id
  http_method = aws_api_gateway_method.register_user_options.http_method
  status_code = aws_api_gateway_method_response.register_user_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = "'${local.allowed_origins}'",
    "method.response.header.Access-Control-Allow-Methods"     = "'GET,OPTIONS,POST,PUT,DELETE'",
    "method.response.header.Access-Control-Allow-Headers"     = "'${local.allowed_headers}'",
    "method.response.header.Access-Control-Allow-Credentials" = "'true'"
  }
}
resource "aws_api_gateway_integration_response" "add_reaction_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.add_reaction_resource.id
  http_method = aws_api_gateway_method.add_reaction_options.http_method
  status_code = aws_api_gateway_method_response.add_reaction_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = "'${local.allowed_origins}'",
    "method.response.header.Access-Control-Allow-Methods"     = "'GET,OPTIONS,POST,PUT,DELETE'",
    "method.response.header.Access-Control-Allow-Headers"     = "'${local.allowed_headers}'",
    "method.response.header.Access-Control-Allow-Credentials" = "'true'"
  }
}
resource "aws_api_gateway_integration_response" "remove_reaction_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id
  resource_id = aws_api_gateway_resource.remove_reaction_resource.id
  http_method = aws_api_gateway_method.remove_reaction_options.http_method
  status_code = aws_api_gateway_method_response.remove_reaction_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = "'${local.allowed_origins}'",
    "method.response.header.Access-Control-Allow-Methods"     = "'GET,OPTIONS,POST,PUT,DELETE'",
    "method.response.header.Access-Control-Allow-Headers"     = "'${local.allowed_headers}'",
    "method.response.header.Access-Control-Allow-Credentials" = "'true'"
  }
}

# Deploy API Gateway
resource "aws_api_gateway_deployment" "photo_ranker_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.create_session_lambda_integration,
    aws_api_gateway_integration.edit_session_lambda_integration,
    aws_api_gateway_integration.get_session_lambda_integration,
    aws_api_gateway_integration.delete_session_lambda_integration,
    aws_api_gateway_integration.create_session_options_integration,
    aws_api_gateway_integration.edit_session_options_integration,
    aws_api_gateway_integration.get_session_options_integration,
    aws_api_gateway_integration.delete_session_options_integration,
    aws_api_gateway_method_response.create_session_response,
    aws_api_gateway_method_response.edit_session_response,
    aws_api_gateway_method_response.get_session_response,
    aws_api_gateway_method_response.delete_session_response,
    aws_api_gateway_method_response.create_session_options_response,
    aws_api_gateway_method_response.edit_session_options_response,
    aws_api_gateway_method_response.get_session_options_response,
    aws_api_gateway_method_response.delete_session_options_response,
    aws_api_gateway_integration_response.create_session_options_integration_response,
    aws_api_gateway_integration_response.edit_session_options_integration_response,
    aws_api_gateway_integration_response.get_session_options_integration_response,
    aws_api_gateway_integration_response.delete_session_options_integration_response,
    aws_api_gateway_integration.register_user_lambda_integration,
    aws_api_gateway_integration.register_user_options_integration,
    aws_api_gateway_method_response.register_user_response,
    aws_api_gateway_method_response.register_user_options_response,
    aws_api_gateway_integration_response.register_user_options_integration_response,
    aws_api_gateway_integration.add_reaction_lambda_integration,
    aws_api_gateway_integration.remove_reaction_lambda_integration,
    aws_api_gateway_integration.add_reaction_options_integration,
    aws_api_gateway_integration.remove_reaction_options_integration,
    aws_api_gateway_method_response.add_reaction_response,
    aws_api_gateway_method_response.remove_reaction_response,
    aws_api_gateway_method_response.add_reaction_options_response,
    aws_api_gateway_method_response.remove_reaction_options_response,
    aws_api_gateway_integration_response.add_reaction_options_integration_response,
    aws_api_gateway_integration_response.remove_reaction_options_integration_response
  ]

  rest_api_id = aws_api_gateway_rest_api.photo_ranker_api.id

  lifecycle {
    create_before_destroy = true
  }

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.photo_ranker_api.id,
      aws_api_gateway_method.create_session_method.id,
      aws_api_gateway_method.edit_session_method.id,
      aws_api_gateway_method.delete_session_method.id,
      aws_api_gateway_method.get_session_method.id,
      aws_api_gateway_method.create_session_options.id,
      aws_api_gateway_method.edit_session_options.id,
      aws_api_gateway_method.get_session_options.id,
      aws_api_gateway_method.delete_session_options.id,
      aws_api_gateway_method.register_user_method.id,
      aws_api_gateway_method.register_user_options.id,
      aws_api_gateway_method.add_reaction_method.id,
      aws_api_gateway_method.remove_reaction_method.id,
      aws_api_gateway_method.add_reaction_options.id,
      aws_api_gateway_method.remove_reaction_options.id
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
resource "aws_lambda_permission" "api_gateway_invoke_edit_session" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.edit_session.function_name
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
resource "aws_lambda_permission" "api_gateway_invoke_delete_session" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.delete_session.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.photo_ranker_api.execution_arn}/*/*"
}
resource "aws_lambda_permission" "api_gateway_invoke_register_user" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.register_user.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.photo_ranker_api.execution_arn}/*/*"
}
resource "aws_lambda_permission" "api_gateway_invoke_add_reaction" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.add_reaction.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.photo_ranker_api.execution_arn}/*/*"
}
resource "aws_lambda_permission" "api_gateway_invoke_remove_reaction" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remove_reaction.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.photo_ranker_api.execution_arn}/*/*"
}