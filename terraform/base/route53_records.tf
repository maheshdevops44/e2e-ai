resource "aws_route53_record" "service_internal" {
  for_each = toset(["ui", "agent", "test-executor", "platform"])

  # Use subdomains under the ACM base: <service>.<project>-<env>.<root>
  # - ui is hosted at the root: <project>-<env>.<root>
  # - others are subdomains: <service>.<project>-<env>.<root>
  name = each.value == "ui" ? "${var.project_name}-${var.environment}" : "${each.value}.${var.project_name}-${var.environment}"
  type    = "A"
  zone_id = data.aws_route53_zone.private_hosted_zone_evernorth.id
  allow_overwrite = true

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

output "service_urls" {
  description = "Private DNS URLs for UI, agent, and test-executor services"
  value = {
    for key, record in aws_route53_record.service_internal : key => "https://${record.fqdn}"
  }
}
