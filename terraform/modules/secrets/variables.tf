variable "region" {
  description = "AWS region where the secrets will be created"
  type        = string
}

variable "secret_name" {
  description = "Name of the Secrets Manager secret"
  type        = string
}

variable "django_secret_key" {
  description = "Django secret key for the application"
  type        = string
}

variable "database_name" {
  description = "Database name for the application"
  type        = string
}

variable "database_endpoint" {
  description = "Database endpoint"
  type        = string
}

variable "database_user" {
  description = "Database user for the application"
  type        = string
}

variable "database_password" {
  description = "Database password for the application"
  type        = string
}

variable "debug" {
  description = "Debug mode for Django (True/False)"
  type        = string
}

variable "environment" {
  description = "Environment tag for resources (e.g., dev, prod)"
  type        = string
}

variable "deploy_key" {
  description = "SSH Key that can check out the target repo"
  type = string
}

variable "project_path" {
  description = "Navigation from outside the repo to inside the repo e.g. myrepo/django_server"
  type = string
  default = "WeddingWebsite/wedding_website"
}

variable "hostname" {
  description = "Website hostname"
  type = string
}

variable "hosted_zone_id" {
  description = "Hosted Zone ID for the relevant hostname"
  type = string
}

variable "use_staging_cert" {
  description = "If true, connect to LetsEncrypt's staging servers, otherwise use the production servers"
  type        = string
  default     = "false"
}

variable "repository_url" {
  description = "URL of the Git repository containing the Django project"
  type        = string
}

variable "gallery_bucket" {
  description = "S3 bucket name of the gallery bucket"
  type        = string
}

variable "gallery_cloudfront_domain" {
  description = "Cloudfront domain of the gallery"
  type        = string
}

variable "sqlite_backup_bucket" {
  description = "S3 bucket name of the SQLite backup bucket"
  type        = string
}