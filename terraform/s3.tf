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