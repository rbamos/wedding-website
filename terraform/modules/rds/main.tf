# Security Group for RDS
resource "aws_security_group" "rds_sg" {
  name_prefix = "rds-sg"
  description = "Allow access to RDS"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Subnet Group for RDS
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "rds-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "RDS DB Subnet Group"
  }
}

# RDS Instance
resource "aws_db_instance" "rds_instance" {
  allocated_storage    = var.allocated_storage
  engine               = var.engine
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  db_name              = var.database_name
  username             = var.database_user
  password             = var.database_password
  publicly_accessible  = var.publicly_accessible
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name = aws_db_subnet_group.db_subnet_group.name

  tags = {
    Name        = var.instance_name
    Environment = var.environment
  }
}
