# Understand what providers are and when you may need another provider beyond the AWS provider:
# https://developer.hashicorp.com/terraform/language/providers
provider "aws" {
  # Why are we using us-east-1?  TLDR it's the region closest (and therefore with lowest latency) to Cigna on-prem data centers
  # Read more at https://confluence.sys.cigna.com/display/CLOUD/AD%3A+aws-us-east-1+-+Cigna%27s+Primary+North+America+Region
  region = "us-east-1"

  # Why would I want to tag my resources?  See https://confluence.sys.cigna.com/display/CLOUD/Development%3A+Tagging#expand-Understandthebenefitsoftagging
  # Often it is easy to forget to add tags to AWS resources.  The following is a way to ensure that all resources are tagged by default.
  default_tags {
    tags = var.cigna_tags
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0" # See the latest version here https://registry.terraform.io/providers/hashicorp/aws/latest
      # Moreover, understand the implications of versioning constraining here https://developer.hashicorp.com/terraform/language/expressions/version-constraints
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.5"
    }
  }

  backend "s3" {} # This is configured at the `backends/` folder.  See README.md for more details
}