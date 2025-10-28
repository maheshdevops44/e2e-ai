# TODO: Complete the instructions here to properly get a CIDR range that can extend the Cigna network: 
# https://confluence.sys.cigna.com/display/CLOUD/Development%3A+Cigna+Networking#Development:CignaNetworking-StepstosetupconnectivitytootherCignaAWSaccounts&on-premresources%E2%9C%85
vpc_routable_cidr_range = "10.192.38.192/27"

vpc_multi_az_flag = false

environment = "dev"

# ECS Configuration
ecs_cpu           = 256
ecs_memory        = 512

test_executor_cpu = 1024
test_executor_memory = 2048

ecs_desired_count = 1
ui_port           = 3000
platform_port     = 3000
api_port          = 8080
agent_port = 8000
health_check_path = "/health"
log_retention_days = 7

aurora_instance_class = "db.r6g.large"

deployer_role_name = "E2eAiDeployer"
project_name = "e2e-ai"

account_id = "745805182138"

dynamodb_billing_mode = "PROVISIONED"
dynamodb_read_capacity = 12
dynamodb_write_capacity = 12
dynamodb_point_in_time_recovery = true

# ACM Certificate Configuration
create_acm_cert = true
acm_domain_name = "e2e-ai-dev.hs-spe2eqa-dev.aws.evernorthcloud.com"
acm_alternative_names = ["*.e2e-ai-dev.hs-spe2eqa-dev.aws.evernorthcloud.com"]

# For Agent
agent_openai_api_type       = "azure"
agent_azure_openai_endpoint = "https://aigateway-prod.apps-1.gp-1-prod.openshift.cignacloud.com/api/v1/ai/GenAIExplorationLab/OAI"
agent_azure_deployment      = "ai-coe-gpt41"
agent_api_version           = "2023-05-15"
agent_opensearch_url        = "https://search-e2e-docs-bsw6zcxgv26ndegiacp44nd4oe.us-east-1.es.amazonaws.com"
agent_opensearch_index      = "intake_index_version_2"
agent_opensearch_username   = "e2e-user-dev"
agent_lan_id                = "C9G5JS"
