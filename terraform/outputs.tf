output "ec2_instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = module.ec2.ec2_instance_public_ip
}

output "secrets_arn" {
  description = "ARN of the AWS Secrets Manager secret"
  value       = module.secrets.secret_arn
}