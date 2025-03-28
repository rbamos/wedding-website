output "vpc_id" {
  value       = aws_vpc.main.id
  description = "The ID of the VPC"
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private_subnets[*].id
}

output "subnet_id" {
  value       = aws_subnet.public_subnet.id
  description = "The ID of the public subnet"
}
