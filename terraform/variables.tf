data "aws_caller_identity" "current" {}

variable "db_user" {}
variable "db_password" {}
variable "auth0_domain" {}
variable "api_audience" {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
}

output "account_id" {
  value = local.aws_account_id
}