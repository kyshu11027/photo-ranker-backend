data "aws_caller_identity" "current" {}

locals {
    aws_account_id = data.aws_caller_identity.current.account_id
}

output "account_id" {
    value = local.aws_account_id
}