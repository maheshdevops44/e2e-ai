resource "aws_secretsmanager_secret" "agent_opensearch_password" {
  name                    = "${var.project_name}/${local.environment}/agent/OPENSEARCH_PASSWORD"
  description             = "OPENSEARCH_PASSWORD for agent service"
  recovery_window_in_days = 0

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-agent-opensearch-password"
    Environment = local.environment
  })
}

resource "aws_secretsmanager_secret" "agent_openai_api_key" {
  name                    = "${var.project_name}/${local.environment}/agent/OPENAI_API_KEY"
  description             = "OPENAI_API_KEY for agent service"
  recovery_window_in_days = 0

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-agent-openai-api-key"
    Environment = local.environment
  })
}

resource "aws_secretsmanager_secret" "agent_lan_password" {
  name                    = "${var.project_name}/${local.environment}/agent/LAN_PASSWORD"
  description             = "LAN_PASSWORD for agent service"
  recovery_window_in_days = 0

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-agent-lan-password"
    Environment = local.environment
  })
}

resource "aws_secretsmanager_secret" "agent_oracle_db_password" {
  name                    = "${var.project_name}/${local.environment}/agent/ORACLE_DB_PASSWORD"
  description             = "Oracle database password for agent service"
  recovery_window_in_days = 0

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-agent-oracle-db-password"
    Environment = local.environment
  })
}

resource "aws_secretsmanager_secret" "aurora_master_password" {
  name                    = "${var.project_name}/${local.environment}/aurora/MASTER_PASSWORD"
  description             = "Master password for ${var.project_name} Aurora PostgreSQL cluster"
  recovery_window_in_days = 0

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-aurora-master-password"
    Environment = local.environment
  })
}