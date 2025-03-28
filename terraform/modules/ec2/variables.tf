variable "region" {
  description = "AWS region where the resources will be created"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "Instance type for the EC2 instance"
  type        = string
  default     = "t2.micro"
}

variable "security_group_name" {
  description = "Name of the security group for the EC2 instance"
  type        = string
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the EC2 instance will be deployed"
  type        = string
}

variable "environment_secrets" {
  description = "Secret ID for environment secrets"
  type = string
}

variable "environment_secrets_arn" {
  description = "Secret arn for environment secrets"
  type = string
}

variable "hostname" {
  description = "Hostname for the server"
  type = string
}

variable "subnet_id" {
  description = "The ID of the subnet to launch the instance in"
  type        = string
}

variable "access_ip" {
  description = "Your access machine's public IP address with CIDR block"
  type        = string
  default     = "0.0.0.0/32" # Replace with your actual IP
}

variable "gallery_bucket" {
  description = "Name of the S3 bucket for gallery files"
  type        = string
}

variable "sqlite_backup_bucket" {
  description = "Name of the S3 bucket for sqlite backups"
  type        = string
}