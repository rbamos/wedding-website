# Secrets Manager secret
resource "aws_secretsmanager_secret" "django_secrets" {
  name        = var.secret_name
  description = "Django environment secrets for the application"

  tags = {
    Environment = var.environment
  }
}

# Secret value
resource "aws_secretsmanager_secret_version" "django_secrets_version" {
  secret_id = aws_secretsmanager_secret.django_secrets.id
  secret_string = jsonencode({
    DJANGO_SECRET_KEY = var.django_secret_key
    DATABASE_NAME     = var.database_name
    DATABASE_USER     = var.database_user
    DATABASE_PASSWORD = var.database_password
    DATABASE_ENDPOINT = var.database_endpoint
    DEBUG             = var.debug
    ENVIRONMENT       = "production"
    DEPLOY_KEY        = var.deploy_key
    PROJECT_PATH      = var.project_path
    HOSTNAME          = var.hostname
    HOSTED_ZONE_ID    = var.hosted_zone_id
    STAGING_CERT      = var.use_staging_cert
    REPOSITORY_URL    = var.repository_url
    GALLERY_BUCKET    = var.gallery_bucket
    GALLERY_CLOUDFRONT_DOMAIN = var.gallery_cloudfront_domain
    SQLITE_BACKUP_BUCKET = var.sqlite_backup_bucket
  })
}
