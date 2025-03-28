output "ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.django_server.id
}

output "ec2_instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.django_server.public_ip
}

output "ec2_instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.django_server.public_dns
}
