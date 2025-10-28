resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${local.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      log_configuration {
        cloud_watch_log_group_name     = aws_cloudwatch_log_group.ecs_exec.name
        cloud_watch_encryption_enabled = true
      }
    }
  }

  tags = merge(
    var.cigna_tags,
    {
      Name        = "${var.project_name}-${local.environment}-cluster"
      Description = "ECS Cluster for ${var.project_name}"
      Environment = local.environment
    }
  )
}

resource "aws_cloudwatch_log_group" "ecs_exec" {
  name              = "/ecs/${var.project_name}-${local.environment}-exec"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cmk.arn

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ecs-exec-logs"
    Environment = local.environment
  })
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}


resource "aws_cloudwatch_log_group" "ui" {
  name              = "/ecs/${var.project_name}-${local.environment}-ui"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cmk.arn

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ui-logs"
    Environment = local.environment
  })
}

resource "aws_cloudwatch_log_group" "platform" {
  name              = "/ecs/${var.project_name}-${local.environment}-platform"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cmk.arn

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-platform-logs"
    Environment = local.environment
  })
}

resource "aws_ecs_task_definition" "ui" {
  family                   = "${var.project_name}-${local.environment}-ui-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "ui"
      image     = "${aws_ecr_repository.ui.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = var.ui_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ui.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "ecs"
        }
      }

      environment = [
        {
          name  = "ENVIRONMENT"
          value = local.environment
        },
        {
          name  = "NEXTAUTH_URL"
          value = "https://${aws_route53_record.service_internal["ui"].fqdn}"
        },
        {
          name  = "AUTH_TRUST_HOST"
          value = "https://${aws_route53_record.service_internal["ui"].fqdn}"
        },
        {
          name  = "NEXT_PUBLIC_SITE_URL"
          value = "https://${aws_route53_record.service_internal["ui"].fqdn}"
        },
        {
          name  = "AWS_REGION"
          value = data.aws_region.current.name
        },
        {
          name  = "NODE_ENV"
          value = "production"
        },
        {
          name  = "AGENT_URL"
          value = "https://${aws_route53_record.service_internal["agent"].fqdn}"
        },
        {
          name  = "TEST_EXECUTOR_URL"
          value = "https://${aws_route53_record.service_internal["test-executor"].fqdn}"
        },
        {
          name  = "ARTIFACTS_BUCKET"
          value = aws_s3_bucket.artifacts.bucket
        },
        {
          name  = "OPENAI_API_TYPE"
          value = var.agent_openai_api_type
        },
        {
          name  = "AZURE_OPENAI_ENDPOINT"
          value = var.agent_azure_openai_endpoint
        },
        {
          name  = "AZURE_DEPLOYMENT"
          value = var.agent_azure_deployment
        },
        {
          name  = "API_VERSION"
          value = var.agent_api_version
        },
        {
          name  = "DB_HOST"
          value = aws_rds_cluster.aurora.endpoint
        },
        {
          name  = "DB_PORT"
          value = "5432"
        },
        {
          name  = "DB_DATABASE"
          value = aws_rds_cluster.aurora.database_name
        },
        {
          name  = "DB_USERNAME"
          value = var.aurora_master_username
        }
      ]

      secrets = [
        {
          name      = "AUTH_SECRET"
          valueFrom = aws_secretsmanager_secret.auth_secret.arn
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_secretsmanager_secret.agent_openai_api_key.arn
        },
        {
          name      = "DB_PASSWORD"
          valueFrom = aws_secretsmanager_secret.aurora_master_password.arn
        }
      ]
    }
  ])

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ui-task-def"
    Environment = local.environment
  })
}

resource "aws_ecs_task_definition" "platform" {
  family                   = "${var.project_name}-${local.environment}-platform-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "platform"
      image     = "${aws_ecr_repository.platform.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = var.platform_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.platform.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "ecs"
        }
      }

      environment = [
        {
          name  = "ENVIRONMENT"
          value = local.environment
        },
        {
          name  = "NEXTAUTH_URL"
          value = "https://${aws_route53_record.service_internal["platform"].fqdn}"
        },
        {
          name  = "AUTH_TRUST_HOST"
          value = "https://${aws_route53_record.service_internal["platform"].fqdn}"
        },
        {
          name  = "NEXT_PUBLIC_SITE_URL"
          value = "https://${aws_route53_record.service_internal["platform"].fqdn}"
        },
        {
          name  = "AWS_REGION"
          value = data.aws_region.current.name
        },
        {
          name  = "NODE_ENV"
          value = "production"
        },
        {
          name  = "AGENT_URL"
          value = "https://${aws_route53_record.service_internal["agent"].fqdn}"
        },
        {
          name  = "TEST_EXECUTOR_URL"
          value = "https://${aws_route53_record.service_internal["test-executor"].fqdn}"
        },
        {
          name  = "ARTIFACTS_BUCKET"
          value = aws_s3_bucket.artifacts.bucket
        },
        {
          name  = "OPENAI_API_TYPE"
          value = var.agent_openai_api_type
        },
        {
          name  = "AZURE_OPENAI_ENDPOINT"
          value = var.agent_azure_openai_endpoint
        },
        {
          name  = "AZURE_DEPLOYMENT"
          value = var.agent_azure_deployment
        },
        {
          name  = "API_VERSION"
          value = var.agent_api_version
        },
        {
          name  = "DB_HOST"
          value = aws_rds_cluster.aurora.endpoint
        },
        {
          name  = "DB_PORT"
          value = "5432"
        },
        {
          name  = "DB_DATABASE"
          value = aws_rds_cluster.aurora.database_name
        },
        {
          name  = "DB_USERNAME"
          value = var.aurora_master_username
        }
      ]

      secrets = [
        {
          name      = "AUTH_SECRET"
          valueFrom = aws_secretsmanager_secret.auth_secret.arn
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_secretsmanager_secret.agent_openai_api_key.arn
        },
        {
          name      = "DB_PASSWORD"
          valueFrom = aws_secretsmanager_secret.aurora_master_password.arn
        }
      ]
    }
  ])

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-platform-task-def"
    Environment = local.environment
  })
}

resource "aws_security_group" "ecs_ui_tasks" {
  name_prefix = "${var.project_name}-${local.environment}-ecs-ui-tasks"
  vpc_id      = module.vpc.id

  ingress {
    protocol        = "tcp"
    from_port       = var.ui_port
    to_port         = var.ui_port
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ecs-ui-tasks"
    Environment = local.environment
  })
}

resource "aws_security_group" "ecs_platform_tasks" {
  name_prefix = "${var.project_name}-${local.environment}-ecs-platform-tasks"
  vpc_id      = module.vpc.id

  ingress {
    protocol        = "tcp"
    from_port       = var.platform_port
    to_port         = var.platform_port
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ecs-platform-tasks"
    Environment = local.environment
  })
}

resource "aws_ecs_service" "ui" {
  name            = "${var.project_name}-${local.environment}-ui-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.ui.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"
  enable_execute_command = true

  network_configuration {
    security_groups  = [aws_security_group.ecs_ui_tasks.id]
    subnets          = [for subnet in flatten(values(module.vpc.subnets_non_routable_by_az)) : subnet.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ui.arn
    container_name   = "ui"
    container_port   = var.ui_port
  }

  depends_on = [
    aws_lb_listener.web_https
  ]

  tags = merge(
    var.cigna_tags,
    {
      Name        = "${var.project_name}-${local.environment}-ui-service"
      Description = "ECS Service for ${var.project_name} UI"
      Environment = local.environment
    }
  )
}

resource "aws_ecs_service" "platform" {
  name            = "${var.project_name}-${local.environment}-platform-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.platform.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"
  enable_execute_command = true

  network_configuration {
    security_groups  = [aws_security_group.ecs_platform_tasks.id]
    subnets          = [for subnet in flatten(values(module.vpc.subnets_non_routable_by_az)) : subnet.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.platform.arn
    container_name   = "platform"
    container_port   = var.platform_port
  }

  depends_on = [
    aws_lb_listener.web_https,
    aws_lb_listener_rule.platform,
    aws_lb_listener_rule.ui
  ]

  tags = merge(
    var.cigna_tags,
    {
      Name        = "${var.project_name}-${local.environment}-platform-service"
      Description = "ECS Service for ${var.project_name} Platform UI"
      Environment = local.environment
    }
  )
}

resource "aws_cloudwatch_log_group" "agent" {
  name              = "/ecs/${var.project_name}-${local.environment}-agent"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cmk.arn

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-agent-logs"
    Environment = local.environment
  })
}

resource "aws_ecs_task_definition" "agent" {
  family                   = "${var.project_name}-${local.environment}-agent-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "agent"
      image     = "${aws_ecr_repository.agent.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = var.agent_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.agent.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "ecs"
        }
      }

      environment = [
        {
          name  = "ENVIRONMENT"
          value = local.environment
        },
        {
          name  = "LAN_ID"
          value = var.agent_lan_id
        },
        {
          name  = "OPENAI_API_TYPE"
          value = var.agent_openai_api_type
        },
        {
          name  = "AZURE_OPENAI_ENDPOINT"
          value = var.agent_azure_openai_endpoint
        },
        {
          name  = "AZURE_DEPLOYMENT"
          value = var.agent_azure_deployment
        },
        {
          name  = "API_VERSION"
          value = var.agent_api_version
        },
        {
          name  = "OPENSEARCH_URL"
          value = var.agent_opensearch_url
        },
        {
          name  = "OPENSEARCH_INDEX"
          value = var.agent_opensearch_index
        },
        {
          name  = "OPENSEARCH_USERNAME"
          value = var.agent_opensearch_username
        },
        {
          name  = "ORACLE_DB_USER"
          value = var.agent_oracle_db_user
        },
        {
          name  = "ORACLE_DB_HOST"
          value = var.agent_oracle_db_host
        },
        {
          name  = "ORACLE_DB_PORT"
          value = var.agent_oracle_db_port
        },
        {
          name  = "ORACLE_DB_SERVICE_NAME"
          value = var.agent_oracle_db_service_name
        }
      ]

      secrets = [
        {
          name      = "OPENSEARCH_PASSWORD"
          valueFrom = aws_secretsmanager_secret.agent_opensearch_password.arn
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_secretsmanager_secret.agent_openai_api_key.arn
        },
        {
          name      = "LAN_PASSWORD"
          valueFrom = aws_secretsmanager_secret.agent_lan_password.arn
        },
        {
          name      = "ORACLE_DB_PASSWORD"
          valueFrom = aws_secretsmanager_secret.agent_oracle_db_password.arn
        }
      ]
    }
  ])

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-agent-task-def"
    Environment = local.environment
  })
}

resource "aws_security_group" "ecs_agent_tasks" {
  name_prefix = "${var.project_name}-${local.environment}-ecs-agent-tasks"
  vpc_id      = module.vpc.id

  ingress {
    protocol        = "tcp"
    from_port       = var.agent_port
    to_port         = var.agent_port
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ecs-agent-tasks"
    Environment = local.environment
  })
}

resource "aws_ecs_service" "agent" {
  name            = "${var.project_name}-${local.environment}-agent-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.agent.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"
  enable_execute_command = true

  network_configuration {
    security_groups  = [aws_security_group.ecs_agent_tasks.id]
    subnets          = [for subnet in flatten(values(module.vpc.subnets_non_routable_by_az)) : subnet.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.agent.arn
    container_name   = "agent"
    container_port   = var.agent_port
  }

  depends_on = [
    aws_lb_listener.web_https,
    aws_lb_listener_rule.agent,
    aws_lb_listener_rule.ui

  ]

  tags = merge(
    var.cigna_tags,
    {
      Name        = "${var.project_name}-${local.environment}-agent-service"
      Description = "ECS Service for ${var.project_name} Agent"
      Environment = local.environment
    }
  )
}

resource "aws_cloudwatch_log_group" "test_executor" {
  name              = "/ecs/${var.project_name}-${local.environment}-test-executor"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cmk.arn

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-test-executor-logs"
    Environment = local.environment
  })
}

resource "aws_ecs_task_definition" "test_executor" {
  family                   = "${var.project_name}-${local.environment}-test-executor-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.test_executor_cpu
  memory                   = var.test_executor_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "test-executor"
      image     = "${aws_ecr_repository.test_executor.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = var.test_executor_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.test_executor.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "ecs"
        }
      }

      environment = [
        {
          name  = "ENVIRONMENT"
          value = local.environment
        },
        {
          name  = "ENV"
          value = local.environment
        },
        {
          name  = "AWS_REGION"
          value = data.aws_region.current.name
        },
        {
          name  = "S3_BUCKET_ID"
          value = aws_s3_bucket.artifacts.bucket
        },
        {
          name  = "LAN_ID"
          value = var.agent_lan_id
        },
        {
          name  = "DB_ENDPOINT"
          value = aws_rds_cluster.aurora.endpoint
        },
        {
          name  = "DB_DATABASE_NAME"
          value = aws_rds_cluster.aurora.database_name
        },
        {
          name  = "DB_USERNAME"
          value = var.aurora_master_username
        },
        {
          name  = "DB_PORT"
          value = "5432"
        }
      ]

      secrets = [
        {
          name      = "LAN_PASSWORD"
          valueFrom = aws_secretsmanager_secret.agent_lan_password.arn
        },
        {
          name      = "DB_PASSWORD"
          valueFrom = aws_secretsmanager_secret.aurora_master_password.arn
        }
      ]
    }
  ])

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-test-executor-task-def"
    Environment = local.environment
  })
}

resource "aws_security_group" "ecs_test_executor_tasks" {
  name_prefix = "${var.project_name}-${local.environment}-ecs-test-executor-tasks"
  vpc_id      = module.vpc.id

  ingress {
    protocol        = "tcp"
    from_port       = var.test_executor_port
    to_port         = var.test_executor_port
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ecs-test-executor-tasks"
    Environment = local.environment
  })
}

resource "aws_ecs_service" "test_executor" {
  name            = "${var.project_name}-${local.environment}-test-executor-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.test_executor.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"
  enable_execute_command = true

  network_configuration {
    security_groups  = [aws_security_group.ecs_test_executor_tasks.id]
    subnets          = [for subnet in flatten(values(module.vpc.subnets_non_routable_by_az)) : subnet.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.test_executor.arn
    container_name   = "test-executor"
    container_port   = var.test_executor_port
  }

  depends_on = [
    aws_lb_listener.web_https,
    aws_lb_listener_rule.test_executor,
  ]

  tags = merge(
    var.cigna_tags,
    {
      Name        = "${var.project_name}-${local.environment}-test-executor-service"
      Description = "ECS Service for ${var.project_name} Test Executor"
      Environment = local.environment
    }
  )
} 