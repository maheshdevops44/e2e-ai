# TODO: Complete the instructions here to properly get a CIDR range that can extend the Cigna network: 
# https://confluence.sys.cigna.com/display/CLOUD/Development%3A+Cigna+Networking#Development:CignaNetworking-StepstosetupconnectivitytootherCignaAWSaccounts&on-premresources%E2%9C%85
vpc_routable_cidr_range = "10.0.0.0/25"

vpc_multi_az_flag = false

environment = "test"

# ECS Configuration
ecs_cpu           = 512
ecs_memory        = 1024
ecs_desired_count = 2
platform_port     = 3000
api_port          = 8080
health_check_path = "/health"
log_retention_days = 14

aurora_instance_class = "db.r6g.2xlarge"

deployer_role_name = "E2eAiDeployer"
project_name = "e2e-ai"

dynamodb_billing_mode = "PROVISIONED"
dynamodb_read_capacity = 20
dynamodb_write_capacity = 20
dynamodb_point_in_time_recovery = true

# ACM Certificate Configuration
create_acm_cert = true
acm_domain_name = "e2e-ai-test.hs-spe2eqa-test.aws.evernorthcloud.com"
acm_alternative_names = ["*.e2e-ai-test.hs-spe2eqa-test.aws.evernorthcloud.com"]