output "api_gateway_url" {
  value       = aws_api_gateway_deployment.photo_ranker_api_deployment.invoke_url
  description = "API Gateway endpoint for the upload function"
}