variable "region" {
  description = "AWS region where the resources will be created"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the website"
  type        = string
}

variable "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  type        = string
}

variable "photos_domain_name" {
  description  = "Domain name of the photos cloudfront distribution"
  type         = string
}