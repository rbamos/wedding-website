provider "aws" {
  region = var.region
}

# S3 backend allows us to manage Terraform from multiple machine
# Make sure the terraform in terraform/backend is run first
terraform {
  backend "s3" {
    bucket         = var.terraform_bucket_name
    key            = "terraform/state/website.tfstate"
    region         = "us-east-1"
    dynamodb_table = var.terraform_lock_table_name
    encrypt        = true
  }
}

data "local_file" "deploy_key_file" {
  filename = "${path.module}/secrets/${var.deploy_key_file}"
}

locals {
  deploy_key = data.local_file.deploy_key_file.content
}

data "local_file" "database_password_file" {
  filename = "${path.module}/secrets/${var.database_password_file}"
}

locals {
  database_password = chomp(replace(data.local_file.database_password_file.content, "\r", ""))
}

data "local_file" "django_secret_key_file" {
  filename = "${path.module}/secrets/${var.django_secret_key_file}"
}

locals {
  django_secret_key = replace(data.local_file.django_secret_key_file.content, "\r", "")
}

data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
}

locals {
  myip = var.access_ip == "" ? "${chomp(data.http.myip.response_body)}/32" : var.access_ip
}

module "ec2" {
  source             = "./modules/ec2"
  region             = var.region
  ami_id             = var.ami_id
  instance_type      = var.instance_type
  security_group_name = var.security_group_name
  instance_name      = var.instance_name
  vpc_id             = module.vpc.vpc_id
  environment_secrets = module.secrets.secret_name
  environment_secrets_arn = module.secrets.secret_arn
  hostname           = var.domain_name
  subnet_id          = module.vpc.subnet_id
  access_ip          = local.myip
  gallery_bucket = module.cloudfront-gallery.bucket_name
  sqlite_backup_bucket = var.sqlite_backup_bucket_name
}

module "vpc" {
  source = "./modules/vpc"
}

module "route53" {
  source       = "./modules/route53"
  region       = var.region
  domain_name  = var.domain_name
  ec2_public_ip = module.ec2.ec2_instance_public_ip
  photos_domain_name = module.cloudfront-gallery.cloudfront_domain_name
}

module "secrets" {
  source           = "./modules/secrets"
  region           = var.region
  secret_name      = var.secret_name
  django_secret_key = local.django_secret_key
  database_name     = var.database_name
  database_endpoint = var.use_rds ? module.rds.rds_instance_endpoint : "sqlite"
  database_user     = var.database_user
  database_password = local.database_password
  debug             = var.debug
  environment       = var.environment
  deploy_key        = local.deploy_key
  hostname          = var.domain_name
  hosted_zone_id    = module.route53.zone_id
  use_staging_cert  = var.use_staging_cert
  repository_url     = var.repository_url
  gallery_bucket = module.cloudfront-gallery.bucket_name
  gallery_cloudfront_domain = "photos.${var.domain_name}"
  sqlite_backup_bucket = var.sqlite_backup_bucket_name
}

module "rds" {
  count               = var.use_rds ? 1 : 0

  source             = "./modules/rds"
  region             = var.region
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnets
  allowed_cidr_blocks = ["10.0.0.0/16"] # Adjust based on your setup
  allocated_storage  = 20
  engine             = "postgres"
  instance_class     = "db.t3.micro"
  database_name      = var.database_name
  database_user      = var.database_user
  database_password  = local.database_password
  publicly_accessible = false
  instance_name      = "django-database"
  environment        = "prod"
}

module "cloudfront-gallery" {
  source      = "./modules/cloudfront_gallery"
  region      = var.region
  bucket_name = var.gallery_bucket_name
  photos_cert_arn = module.route53.photos_cert_arn
  domain_name  = var.domain_name
}
