resource "aws_dynamodb_table" "sessions" {
  name         = "photo-ranker-sessions-${terraform.workspace}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sessionId"

  attribute {
    name = "sessionId"
    type = "S" # String type
  }
  ttl {
    attribute_name = "expirationTime"
    enabled        = true
  }
  tags = {
    Name        = "photo-sessions"
    Environment = "dev"
  }

}