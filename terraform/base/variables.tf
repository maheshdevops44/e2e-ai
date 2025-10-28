# ========== VARIABLES THAT ARE THE SAME BETWEEN ENVIRONMENTS ==========

variable "project_name" {
  description = "The name of the project.  This must be used to prefix the names of all resources."
  type        = string
  default     = "e2e-ai" # TODO: Update this to your project name
}

variable "deployer_role_name" {
  description = "The name of the IAM role that deploys this project in a CICD pipeline."
  type        = string
  default     = "E2eAiDeployer" # TODO: Update this to the name of the role that is allowed to deploy this project
}

variable "cigna_tags" {
  description = "Cigna required tags as described here: https://confluence.sys.cigna.com/display/CLOUD/Cloud+Tagging+Requirements+v2.0"
  type        = map(string) 
  # TODO: Update to the correct values for your workload using the docs above
  default = {
    CostCenter       = "1234567"
    AssetOwner       = "deepankar.nath@evernorth.com"
    ServiceNowBA     = "notAssigned" # See https://confluence.sys.cigna.com/display/CLOUD/ServiceNow%3A+BA+and+AS
    ServiceNowAS     = "notAssigned" # See https://confluence.sys.cigna.com/display/CLOUD/ServiceNow%3A+BA+and+AS
    SecurityReviewID = "RITM123456" # See https://confluence.sys.cigna.com/display/CLOUD/CIP%3A+Submit+CSCA+Form
    P2P              = "RITM123456" # See https://confluence.sys.cigna.com/display/CLOUD/P2P%3A+Start+With+a+Public+Cloud+Intake
  }
}

# ========== VARIABLES THAT CHANGE BETWEEN ENVIRONMENTS ==========

# The values of these variables change per environment, and therefore will have different
# values configured in the environments/dev.tfvars, test.tfvars, and prod.tfvars files

variable "vpc_routable_cidr_range" {
    description = "The requested CIDR range that is compatible to extend the Cigna network.  This must be requested with the following instructions: https://confluence.sys.cigna.com/display/CLOUD/Development%3A+Cigna+Networking#Development:CignaNetworking-StepstosetupconnectivitytootherCignaAWSaccounts&on-premresources%E2%9C%85"
    type        = string
}

variable "vpc_multi_az_flag" {
    description = "A flag to indicate if the given environment should have a multi-AZ NAT gateway deployed in the golden VPC module."
    type = bool
}

variable "environment" {
    description = "The environment name (dev, test, prod)"
    type        = string
}

variable "ecs_cpu" {
    description = "CPU units for ECS task (256, 512, 1024, 2048, 4096)"
    type        = number
    default     = 256
}

variable "ecs_memory" {
    description = "Memory (MiB) for ECS task"
    type        = number
    default     = 512
}

variable "test_executor_cpu" {
    description = "CPU units for ECS task (256, 512, 1024, 2048, 4096)"
    type        = number
    default     = 256
}

variable "test_executor_memory" {
    description = "Memory (MiB) for ECS task"
    type        = number
    default     = 512
}

variable "ecs_desired_count" {
    description = "Desired number of ECS tasks"
    type        = number
    default     = 1
}

variable "aurora_engine_version" {
  description = "Aurora PostgreSQL engine version"
  type        = string
  default     = "15.12"
}

variable "aurora_instance_class" {
  description = "Instance class for Aurora PostgreSQL instances"
  type        = string
  default     = "db.t4g.medium"
}

variable "aurora_master_username" {
  description = "Master username for Aurora PostgreSQL"
  type        = string
  default     = "app_admin"
}


variable "ui_port" {
    description = "Port on which the UI runs"
    type        = number
    default     = 3000
}

variable "platform_port" {
    description = "Port on which the Platform UI runs"
    type        = number
    default     = 3000
}

variable "agent_port" {
    description = "Port on which the agent API runs"
    type        = number
    default     = 8000
}

variable "test_executor_port" {
    description = "Port on which the test-executor API runs"
    type        = number
    default     = 8000
}

variable "health_check_path" {
    description = "Health check path for load balancer"
    type        = string
    default     = "/health"
}

variable "log_retention_days" {
    description = "CloudWatch log retention in days"
    type        = number
    default     = 7
}

## ========== Agent non-secret configuration ==========
variable "agent_openai_api_type" {
  description = "Value for OPENAI_API_TYPE"
  type        = string
  default     = "azure"
}

variable "agent_azure_openai_endpoint" {
  description = "Value for AZURE_OPENAI_ENDPOINT"
  type        = string
  default     = ""
}

variable "agent_azure_deployment" {
  description = "Value for AZURE_DEPLOYMENT"
  type        = string
  default     = ""
}

variable "agent_api_version" {
  description = "Value for API_VERSION"
  type        = string
  default     = ""
}

variable "agent_opensearch_url" {
  description = "Value for OPENSEARCH_URL"
  type        = string
  default     = ""
}

variable "agent_opensearch_index" {
  description = "Value for OPENSEARCH_INDEX"
  type        = string
  default     = ""
}

variable "agent_opensearch_username" {
  description = "Value for OPENSEARCH_USERNAME"
  type        = string
  default     = ""
}

variable "agent_lan_id" {
  description = "Value for LAN_ID"
  type        = string
  default     = ""
}

variable "agent_oracle_db_user" {
  description = "Oracle database username for agent service"
  type        = string
  default     = "RXP88QD_RO"
}

variable "agent_oracle_db_host" {
  description = "Oracle database host for agent service"
  type        = string
  default     = "qr1014661-scan.express-scripts.com"
}

variable "agent_oracle_db_port" {
  description = "Oracle database port for agent service"
  type        = string
  default     = "1521"
}

variable "agent_oracle_db_service_name" {
  description = "Oracle database service name for agent service"
  type        = string
  default     = "QAPHRXP88"
}

variable "create_acm_cert" {
  description = "Whether to create ACM certificate for ALB"
  type        = bool
  default     = false
}

variable "acm_domain_name" {
  description = "Primary domain name for ACM certificate"
  type        = string
  default     = ""
}

variable "acm_alternative_names" {
  description = "Alternative domain names for ACM certificate"
  type        = list(string)
  default     = []
}

# ========== ALB ACCESS LOGGING ==========

variable "alb_access_logs_enabled" {
  description = "Whether to enable ALB access logs"
  type        = bool
  default     = true
}

variable "alb_access_logs_bucket_prefix" {
  description = "S3 bucket prefix for ALB access logs"
  type        = string
  default     = "alb-access-logs"
}

variable "alb_access_logs_retention_days" {
  description = "Number of days to retain ALB access logs in S3"
  type        = number
  default     = 90
}

variable "artifacts_retention_days" {
  description = "Number of days to retain artifacts in S3"
  type        = number
  default     = 365
}

# ========== DYNAMODB CONFIGURATION ==========

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "dynamodb_read_capacity" {
  description = "DynamoDB read capacity units (only used with PROVISIONED billing mode)"
  type        = number
  default     = 5
}

variable "dynamodb_write_capacity" {
  description = "DynamoDB write capacity units (only used with PROVISIONED billing mode)"
  type        = number
  default     = 5
}