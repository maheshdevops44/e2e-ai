output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecr_repository_url_ui" {
  description = "URL of the UI ECR repository"
  value       = aws_ecr_repository.ui.repository_url
}

output "ecr_repository_name_ui" {
  description = "Name of the UI ECR repository"
  value       = aws_ecr_repository.ui.name
}

output "ecs_service_name_ui" {
  description = "Name of the UI ECS service"
  value       = aws_ecs_service.ui.name
}

output "ecs_task_definition_family_ui" {
  description = "Family name of the UI ECS task definition"
  value       = aws_ecs_task_definition.ui.family
}

output "ecr_repository_url_platform" {
  description = "URL of the Platform ECR repository"
  value       = aws_ecr_repository.platform.repository_url
}

output "ecr_repository_name_platform" {
  description = "Name of the Platform ECR repository"
  value       = aws_ecr_repository.platform.name
}

output "ecs_service_name_platform" {
  description = "Name of the Platform ECS service"
  value       = aws_ecs_service.platform.name
}

output "ecs_task_definition_family_platform" {
  description = "Family name of the Platform ECS task definition"
  value       = aws_ecs_task_definition.platform.family
}

output "ecr_repository_url_agent" {
  description = "URL of the Agent ECR repository"
  value       = aws_ecr_repository.agent.repository_url
}

output "ecr_repository_name_agent" {
  description = "Name of the Agent ECR repository"
  value       = aws_ecr_repository.agent.name
}

output "ecs_service_name_agent" {
  description = "Name of the Agent ECS service"
  value       = aws_ecs_service.agent.name
}

output "ecs_task_definition_family_agent" {
  description = "Family name of the Agent ECS task definition"
  value       = aws_ecs_task_definition.agent.family
}

output "vpc_id" {
  description = "ID of the Golden VPC"
  value       = module.vpc.id
}

output "subnets_non_routable_by_az" {
  description = "Object containing lists of all subnet created in the non-routable IP space grouped by availability zone"
  value       = module.vpc.subnets_non_routable_by_az
  sensitive   = true
}

output "subnets_routable_by_az" {
  description = "Object containing lists of all subnet IDs created in the routable IP space, grouped by availability zone"
  value       = module.vpc.subnets_routable_by_az
  sensitive   = true
}

output "transit_gateway_attachment_id" {
  description = "ID of the Transit Gateway attachment"
  value       = module.vpc.transit_gateway_attachment_id
}

output "vpc_endpoints_gateway" {
  description = "VPC gateway endpoints created by the module"
  value       = module.vpc.vpc_endpoints_gateway
  sensitive   = true
}

output "vpc_endpoints_interface_non_routable" {
  description = "Non routable VPC interface endpoints created by the module"
  value       = module.vpc.vpc_endpoints_interface_non_routable
  sensitive   = true
}

output "vpc_endpoints_interface_routable" {
  description = "Routable VPC interface endpoints created by the module"
  value       = module.vpc.vpc_endpoints_interface_routable
}

output "vpc_version" {
  description = "Git tag version of the Golden VPC module"
  value       = module.vpc.version
}

output "load_balancer_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_url" {
  description = "URL to access the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.main.name
  sensitive   = true
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.main.arn
}

output "dynamodb_table_id" {
  description = "ID of the DynamoDB table"
  value       = aws_dynamodb_table.main.id
}

output "aurora_cluster_endpoint" {
  description = "Writer endpoint for the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.aurora.endpoint
}

output "aurora_reader_endpoint" {
  description = "Reader endpoint for the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.aurora.reader_endpoint
}

output "aurora_secret_arn" {
  description = "Secrets Manager ARN storing the Aurora master password"
  value       = aws_secretsmanager_secret.aurora_master_password.arn
  sensitive   = true
}

output "aurora_database_name" {
  description = "The resolved/actual primary database name inside Aurora PostgreSQL. Always in the form project_name_environment."
  value       = aws_rds_cluster.aurora.database_name
}

# ALB Access Logs S3 Bucket Outputs
output "alb_access_logs_bucket_id" {
  description = "ID of the S3 bucket for ALB access logs"
  value       = aws_s3_bucket.alb_access_logs.id
}

output "alb_access_logs_bucket_arn" {
  description = "ARN of the S3 bucket for ALB access logs"
  value       = aws_s3_bucket.alb_access_logs.arn
}

output "artifacts_bucket_name" {
  description = "Name of the S3 bucket for artifacts storage"
  value       = aws_s3_bucket.artifacts.bucket
}

output "artifacts_bucket_arn" {
  description = "ARN of the S3 bucket for artifacts storage"
  value       = aws_s3_bucket.artifacts.arn
}

output "auth_secret_arn" {
  description = "ARN of the AUTH_SECRET in AWS Secrets Manager"
  value       = aws_secretsmanager_secret.auth_secret.arn
  sensitive   = true
}