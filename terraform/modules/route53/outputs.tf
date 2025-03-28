output "zone_id" {
  description = "Route 53 hosted zone ID"
  value       = aws_route53_zone.primary.zone_id
}

output "www_record" {
  description = "Fully qualified domain name (FQDN) for the www record"
  value       = aws_route53_record.www.fqdn
}

output "root_record" {
  description = "Fully qualified domain name (FQDN) for the root redirect"
  value       = aws_route53_record.root_redirect.fqdn
}

output "photos_cert_arn" {
  description = "ARN of the ACM photos certificate"
  value       = aws_acm_certificate.photos_cert.arn
}