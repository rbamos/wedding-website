variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the website"
  type        = string
}

variable "photos_cert_arn" {
  description = "ARN of the ACM photos certificate"
  type        = string
}