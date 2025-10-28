locals {
  aurora_non_routable_by_az = module.vpc.subnets_non_routable_by_az
  aurora_azs_sorted         = sort(keys(local.aurora_non_routable_by_az))
  aurora_primary_az         = local.aurora_azs_sorted[0]

  aurora_subnet_ids = flatten([
    for az in local.aurora_azs_sorted : [
      for subnet in local.aurora_non_routable_by_az[az] : subnet.id
    ]
  ])

  aurora_multi_az_count = min(length(local.aurora_azs_sorted), 2)
  aurora_instance_azs = var.vpc_multi_az_flag ? slice(local.aurora_azs_sorted, 0, local.aurora_multi_az_count) : [local.aurora_primary_az]
}

resource "random_password" "aurora_master" {
  length  = 26
  special = false
}

resource "aws_secretsmanager_secret_version" "aurora_master_password" {
  secret_id     = aws_secretsmanager_secret.aurora_master_password.id
  secret_string = random_password.aurora_master.result
}

resource "aws_rds_cluster_parameter_group" "aurora" {
  family = "aurora-postgresql15"
  name   = "${var.project_name}-${local.environment}-aurora"
  
  parameter {
    name         = "rds.force_ssl"
    value        = "1"
    apply_method = "pending-reboot"
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-aurora-cluster-parameter-group"
    Environment = local.environment
  })
}

resource "aws_db_subnet_group" "aurora" {
  name       = "${var.project_name}-${local.environment}-aurora"
  subnet_ids = local.aurora_subnet_ids

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-aurora-subnet-group"
    Environment = local.environment
  })
}

resource "aws_security_group" "aurora" {
  name_prefix = "${var.project_name}-${local.environment}-aurora"
  description = "Access control for ${var.project_name} Aurora PostgreSQL"
  vpc_id      = module.vpc.id

  ingress {
    description     = "PostgreSQL from UI tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_ui_tasks.id]
  }

  ingress {
    description     = "PostgreSQL from agent tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_agent_tasks.id]
  }

  ingress {
    description     = "PostgreSQL from test-executor tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_test_executor_tasks.id]
  }

  ingress {
    description     = "PostgreSQL from platform tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_platform_tasks.id]
  } 
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-aurora-sg"
    Environment = local.environment
  })
}

resource "aws_rds_cluster" "aurora" {
  cluster_identifier              = "${var.project_name}-${local.environment}-aurora"
  engine                          = "aurora-postgresql"
  engine_version                  = var.aurora_engine_version
  database_name                   = "${replace(var.project_name, "-", "")}${var.environment}"
  master_username                 = var.aurora_master_username
  master_password                 = random_password.aurora_master.result
  db_subnet_group_name            = aws_db_subnet_group.aurora.name
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.aurora.name
  vpc_security_group_ids          = [aws_security_group.aurora.id]
  kms_key_id                      = aws_kms_key.cmk.arn
  storage_encrypted               = true
  copy_tags_to_snapshot           = true
  backup_retention_period         = var.vpc_multi_az_flag ? 7 : 1
  preferred_backup_window         = "03:00-04:00"
  preferred_maintenance_window    = "sun:05:00-sun:06:00"
  deletion_protection             = local.environment == "prod"
  skip_final_snapshot             = local.environment != "prod"
  iam_database_authentication_enabled = true
  # enable_http_endpoint            = true

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-aurora-cluster"
    Environment = local.environment
  })
}

resource "aws_rds_cluster_instance" "aurora" {
  count                = length(local.aurora_instance_azs)
  identifier           = "${var.project_name}-${local.environment}-aurora-${count.index + 1}"
  cluster_identifier   = aws_rds_cluster.aurora.id
  instance_class       = var.aurora_instance_class
  engine               = aws_rds_cluster.aurora.engine
  engine_version       = aws_rds_cluster.aurora.engine_version
  db_subnet_group_name = aws_db_subnet_group.aurora.name
  availability_zone    = local.aurora_instance_azs[count.index]
  promotion_tier       = count.index + 1
  publicly_accessible  = false
  apply_immediately    = true

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-aurora-instance-${count.index + 1}"
    Environment = local.environment
  })
}

