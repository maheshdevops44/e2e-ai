# Avoid ever hardcoding the AWS account ID in your Terraform.  Instead, reference your account ID using the following snippet that uses this data resource:
data "aws_caller_identity" "current" {}

# Avoid ever hardcoding the AWS region in your Terraform.  Instead, reference your region using the following snippet that uses this data resource:
# data.aws_region.current.name
data "aws_region" "current" {}

# Easy access to the account name (this isn't an AWS specific attribute, rather custom made to help identify within Cigna)
data "aws_ssm_parameter" "account_name" {
  name = "/Enterprise/AccountName"
}

# Easy access to the environment name (this isn't an AWS specific attribute, rather custom made to help identify within Cigna)
data "aws_ssm_parameter" "environment_name" {
  name = "/Enterprise/Environment"
}

# This provides the correct ARN of the alarm funnel for a given environment: https://github.sys.cigna.com/cigna/aws-alarm-funnel
# Can read about why you would need the alarm funnel integrated on a given CloudWatch alarm here https://confluence.sys.cigna.com/display/CLOUD/P2P%3A+FMEA#P2P:FMEA-StepstoconfigurealarmfunnelandimplementCWalarms%E2%9C%85
data "aws_ssm_parameter" "alarm_funnel_arn" {
  name = "/Enterprise/AlarmFunnelArn"
}

# This provides the ARN of the CloudWatch Splunk centralized log group that a given CloudWatch log group can create a subscription filter for
# This is typically done automatically via the mechanism outlined here https://confluence.sys.cigna.com/display/CLOUD/Centralized+Logging+of+All+AWS+Services
data "aws_ssm_parameter" "centralized_logging_arn" {
  name = "/Enterprise/OrgCentralLoggingDestinationArn"
}

# The golden AMI is only relevant if a given workload requires EC2 instances.  Typically, these should be avoided in lieu of 
# cheaper and simpler serverless compute platforms (ex: Lambda, ECS Fargate, Glue).  However, the golden AMI provides a CIP-approved
# version of AWS managed AMIs (in this example, Amazon Linux 3) that is further configured with required Cigna configs (ex: Zscaler certs).
# You can read more about the GAMI here: https://github.sys.cigna.com/cigna/aws-golden-ami-factory/wiki
# data "aws_ssm_parameter" "al3_golden_ami" {
#   name = "/cloud-coe/versions/cigna-golden-ami2023"
# }

# The following two SSM parameters are the public and private Route53 DNS hosted zones that are automatically given to a given AWS account
# Learn more about custom domain names in AWS at Cigna here: https://confluence.sys.cigna.com/display/CLOUD/Development%3A+Cigna+Networking#Development:CignaNetworking-Route53:StepstosetupdomainnamesandDNSresolution%E2%9C%85
# The EVERNORTH hosted zones follow these naming conventions: 
# Private & private hosted zone: <account name>-<env>.aws.evernorthcloud.com
data "aws_ssm_parameter" "public_hosted_zone_evernorth" {
  name = "/Enterprise/EvernorthcloudPublicHostedZoneId"
}

data "aws_ssm_parameter" "private_hosted_zone_evernorth" {
  name = "/Enterprise/EvernorthcloudPrivateHostedZoneId"
}

data "aws_route53_zone" "public_hosted_zone_evernorth" {
  zone_id = data.aws_ssm_parameter.public_hosted_zone_evernorth.value
}

data "aws_route53_zone" "private_hosted_zone_evernorth" {
  zone_id = data.aws_ssm_parameter.private_hosted_zone_evernorth.value
}

# The CIGNA hosted zones follow these naming conventions: 
# Private & private hosted zone: <account name>-<env>.aws.cignacloud.com
data "aws_ssm_parameter" "public_hosted_zone_cigna" {
  name = "/Enterprise/PublicHostedZoneId"
}

data "aws_ssm_parameter" "private_hosted_zone_cigna" {
  name = "/Enterprise/PrivateHostedZoneId"
}

data "aws_route53_zone" "public_hosted_zone_cigna" {
  zone_id = data.aws_ssm_parameter.public_hosted_zone_cigna.value
}

data "aws_route53_zone" "private_hosted_zone_cigna" {
  zone_id = data.aws_ssm_parameter.private_hosted_zone_cigna.value
}

# Understand when you should be keeping your Terraform code DRY by using locals: 
# https://developer.hashicorp.com/terraform/language/values/locals

locals {
    # Helpful dynamic references
    account_id = data.aws_caller_identity.current.account_id
    region = data.aws_region.current.name
    env = data.aws_ssm_parameter.environment_name.value
    environment = var.environment
    account_name = data.aws_ssm_parameter.account_name.value

    # Useful for when CloudWatch alarms are created
    alarm_funnel_arn = data.aws_ssm_parameter.alarm_funnel_arn.value

    # Centralized logging can be used to send a given CloudWatch log group logs to Splunk
    centralized_logging_arn = data.aws_ssm_parameter.centralized_logging_arn.value

    # Golden AMI for EC2 instances (if applicable)
    # al3_golden_ami_id = data.aws_ssm_parameter.al3_golden_ami.value
    
    # Build ALB FQDN (<project>-<environment>.<account-env zone>)
    root_domain       = trim(data.aws_route53_zone.private_hosted_zone_evernorth.name, ".")
    alb_subdomain     = "${var.project_name}-${var.environment}"
    computed_fqdn     = "${local.alb_subdomain}.${local.root_domain}"

    # ACM certificate locals
    acm_name          = var.acm_domain_name != "" ? var.acm_domain_name : local.computed_fqdn
    acm_alternatives  = length(var.acm_alternative_names) > 0 ? var.acm_alternative_names : ["*.${local.computed_fqdn}"]
    create_acm_cert   = var.create_acm_cert
    merged_tags       = var.cigna_tags
    
    # Domain validation options
    domain_validation_options_set = local.create_acm_cert ? aws_acm_certificate.alb_cert[0].domain_validation_options : []
}
