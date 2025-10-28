# Often, enterprises will provide a list of golden modules that can be leveraged with built-in compliance and integrates workloads into the Cigna environmnet
# One of the most popular is the golden VPC module.  This should only be used in the following use cases:
  # - The workload needs connectivity to Cigna on-prem data centers
  # - The workload hosts VPC based AWS resources
  # - The workload hosts VPC based compute resources (ex: Lambda, EC2, Glue jobs) that require connectivity to the Internet
module "vpc" {
  # The "?ref=0.7.7" at the end of the source URL is the version of the golden VPC module to be used
  # Update this with the latest version listed here: https://github.sys.cigna.com/cigna/AWS-GoldenVPC/releases
  source = "git::https://github.sys.cigna.com/cigna/AWS-GoldenVPC?ref=0.7.7"

  # Cigna has a finite number of private IP addresses.  A custom CIDR range must be requested to extend the Cigna network as outlined at environments/dev.tfvars
  cidr_blocks_routable = [var.vpc_routable_cidr_range]
  name_prefix          = "${var.project_name}-${local.env}"
  vpc_gateway_endpoint_services   = ["s3", "dynamodb"] # These gateway endpoints are free and provide private connectivity to these services for the S3 and DynamoDB services: https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html
  vpc_interface_endpoint_services = ["ecr.dkr", "ecr.api", "logs", "ssm", "ssmmessages", "ec2messages"]
  nat_gateway_enabled = true
  transit_gateway_attachment_enabled = true # What is the transit gateway (TGW)?  You can read about how this provides connectivity to Cigna on-prem data centers here: https://confluence.sys.cigna.com/display/CLOUD/Development%3A+Cigna+Networking#expand-LearnmoreaboutCignasnetworkingwithAWS

  nat_gateway_highly_available_enabled = var.vpc_multi_az_flag
  cigna_tags = var.cigna_tags
}

# Outside of the golden VPC module, all other golden modules are optional but can save teams time
# See a complete list of golden modules available here: https://confluence.sys.cigna.com/display/CLOUD/Terraform+Golden+Modules