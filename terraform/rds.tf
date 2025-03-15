resource "aws_db_instance" "photo_ranking_db" {
  identifier             = "photo-ranker-db-${terraform.workspace}"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  max_allocated_storage  = 100
  db_name                = "photoranker"
  username               = var.db_user
  password               = var.db_password
  vpc_security_group_ids = [aws_security_group.db_security.id]
  publicly_accessible    = true
  skip_final_snapshot    = true
}

resource "aws_security_group" "db_security" {
  name_prefix = "photo-db-sg"

  ingress {
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/16"]
  }
}
 