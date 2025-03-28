variable "region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for the RDS instance"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the RDS instance"
  type        = list(string)
}

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the RDS instance"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "allocated_storage" {
  description = "The allocated storage in GB for the RDS instance"
  type        = number
  default     = 20
}

variable "engine" {
  description = "The database engine to use"
  type        = string
  default     = "postgres"
}

variable "engine_version" {
  description = "The version of the database engine"
  type        = string
  default     = "17.2"
}

variable "instance_class" {
  description = "The instance class for the RDS instance"
  type        = string
  default     = "db.t3.micro"
}

variable "database_name" {
  description = "The name of the database"
  type        = string
}

variable "database_user" {
  description = "The username for the database"
  type        = string
}

variable "database_password" {
  description = "The password for the database"
  type        = string
  sensitive   = true
}

variable "publicly_accessible" {
  description = "Whether the database instance is publicly accessible"
  type        = bool
  default     = false
}

variable "instance_name" {
  description = "The name of the RDS instance"
  type        = string
}

variable "environment" {
  description = "Environment tag for the RDS instance"
  type        = string
}

variable "backup_retention_period" {
  description = "The number of days to retain automated backups"
  type        = number
  default     = 7 
}

variable "backup_window" {
  description = "The daily time range during which automated backups are created (in UTC)"
  type        = string
  default     = "04:00-05:00"
}
