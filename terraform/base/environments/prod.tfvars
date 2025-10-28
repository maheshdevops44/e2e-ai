# TODO: Complete the instructions here to properly get a CIDR range that can extend the Cigna network: 
# https://confluence.sys.cigna.com/display/CLOUD/Development%3A+Cigna+Networking#Development:CignaNetworking-StepstosetupconnectivitytootherCignaAWSaccounts&on-premresources%E2%9C%85
vpc_routable_cidr_range = "10.0.0.0/25"

vpc_multi_az_flag = true

environment = "prod"

# ECS Configuration
ecs_cpu           = 1024
ecs_memory        = 2048
ecs_desired_count = 3
platform_port     = 3000
api_port          = 8080
health_check_path = "/health"
log_retention_days = 30

aurora_instance_class = "db.r6g.xlarge"

deployer_role_name = "E2eAiDeployer"
project_name = "e2e-ai"

dynamodb_billing_mode = "PROVISIONED"
dynamodb_read_capacity = 50
dynamodb_write_capacity = 50
dynamodb_point_in_time_recovery = true