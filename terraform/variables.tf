# General Variables
variable "region" {
  description = "AWS region for resource deployment"
  type        = string
}

variable "use_rds" {
  description = "If true, create an RDS instance, otherwise use SQLite"
  type        = bool
  default     = false
}

variable "environment" {
  description = "Environment (e.g., dev, prod)"
  type        = string
}

# EC2 Variables
variable "ami_id" {
  description = "AMI ID for EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "security_group_name" {
  description = "Name of the EC2 security group"
  type        = string
}

variable "instance_name" {
  description = "Name of the EC2 instance"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the EC2 instance is deployed"
  type        = string
}

variable "repository_url" {
  description = "Git repository URL for the Django project"
  type        = string
}

# Route 53 Variables
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

# Secrets Variables
variable "secret_name" {
  description = "Name of the AWS Secrets Manager secret"
  type        = string
}

variable "django_secret_key_file" {
  description = "Django secret key"
  type        = string
}

variable "database_name" {
  description = "Name of the SQLite database"
  type        = string
}

variable "database_user" {
  description = "Database user"
  type        = string
}

variable "database_password_file" {
  description = "The name of the files in secrets/ of the database password file"
  type        = string
}

variable "debug" {
  description = "Django debug mode"
  type        = string
}

variable "deploy_key_file" {
  description = "The name of the files in secrets/ of the ssh key file"
  type        = string
}

variable "terraform_bucket_name" {
  description = "S3 bucket name for Terraform state"
  type        = string
}

variable "terraform_lock_table_name" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
}

variable "noncurrent_transition_days" {
  description = "Days for noncurrent versions to transition to Glacier"
  type        = number
  default     = 30
}

variable "noncurrent_expiration_days" {
  description = "Days for noncurrent versions to expire"
  type        = number
  default     = 365
}

variable "access_ip" {
  description = "Your access machine's public IP address with CIDR block"
  type        = string
  default     = ""
}

variable "use_staging_cert" {
  description = "If true, connect to LetsEncrypt's staging servers, otherwise use the production servers"
  type        = string
  default     = "false"
}

variable "gallery_bucket_name" {
  description = "Name of the S3 bucket for the gallery"
  type        = string
}

variable "sqlite_backup_bucket_name" {
  description = "Name of the S3 bucket for SQLite backups"
  type        = string
}