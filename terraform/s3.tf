resource "aws_s3_bucket" "session_images" {
  bucket = "photo-ranker-images-${terraform.workspace}"
  tags = {
    Name        = "PhotoRankerImages"
    Environment = "${terraform.workspace}"
    Project     = "PhotoRanker"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "session_images_lifecycle" {
  bucket = aws_s3_bucket.session_images.id
  rule {
    id     = "delete-objects"
    status = "Enabled"
    expiration {
      days = 7
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "session_images_cors" {
  bucket = aws_s3_bucket.session_images.id

  cors_rule {
    allowed_origins = terraform.workspace == "dev" ? ["https://pickpix.vercel.app", "http://localhost:3000"] : ["https://pickpix.vercel.app"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_headers = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}