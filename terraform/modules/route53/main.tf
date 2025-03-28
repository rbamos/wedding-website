# Route 53 hosted zone
resource "aws_route53_zone" "primary" {
  name = var.domain_name
}

resource "aws_route53_record" "root_redirect" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = var.domain_name
  type    = "A"
  ttl     = 300
  records = [var.ec2_public_ip]
}

resource "aws_route53_record" "www" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = "www.${var.domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = [var.domain_name]
}

resource "aws_route53_record" "photos_cname" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = "photos.${var.domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = [var.photos_domain_name]
}

resource "aws_acm_certificate" "photos_cert" {
  domain_name       = "photos.${var.domain_name}"
  validation_method = "DNS"
}

# Add a Route 53 DNS validation record
resource "aws_route53_record" "photos_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.photos_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      value  = dvo.resource_record_value
    }
  }

  zone_id = aws_route53_zone.primary.zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.value]
  ttl     = 300
}

resource "aws_acm_certificate_validation" "photos_cert_validation" {
  certificate_arn         = aws_acm_certificate.photos_cert.arn
  validation_record_fqdns = [for r in aws_route53_record.photos_cert_validation : r.fqdn]
}
