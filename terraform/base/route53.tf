resource "aws_route53_record" "app_internal" {
  # Mirrors sample-terraform/modules/route53.tf but targets the internal ALB in the private hosted zone
  name    = "${var.project_name}-${var.environment}"
  type    = "A"
  zone_id = data.aws_route53_zone.private_hosted_zone_evernorth.id
  allow_overwrite = true

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}
