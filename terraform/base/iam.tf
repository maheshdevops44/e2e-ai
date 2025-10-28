resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-${local.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ecs-execution-role"
    Environment = local.environment
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_execution_custom" {
  name = "${var.project_name}-${local.environment}-ecs-execution-custom"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [aws_kms_key.cmk.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = data.aws_region.current.name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents"
        ]
        Resource = [
          "${aws_cloudwatch_log_group.ui.arn}:*",
          "${aws_cloudwatch_log_group.platform.arn}:*",
          "${aws_cloudwatch_log_group.agent.arn}:*",
          "${aws_cloudwatch_log_group.test_executor.arn}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.auth_secret.arn,
          aws_secretsmanager_secret.agent_opensearch_password.arn,
          aws_secretsmanager_secret.agent_openai_api_key.arn,
          aws_secretsmanager_secret.agent_lan_password.arn,
          aws_secretsmanager_secret.agent_oracle_db_password.arn,
          aws_secretsmanager_secret.aurora_master_password.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-${local.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ecs-task-role"
    Environment = local.environment
  })
}

resource "aws_iam_role_policy" "ecs_task_exec_logs" {
  name = "${var.project_name}-${local.environment}-ecs-task-exec-logs"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = data.aws_region.current.name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents"
        ]
        Resource = [
          "${aws_cloudwatch_log_group.ecs_exec.arn}:*"
        ]
      }
    ]
  })
}

# resource "aws_iam_policy" "ecs_task_deletion_custom" {
#   name = "${var.project_name}-${local.environment}-ecs-task-deletion-custom"

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "ecs:DeregisterTaskDefinition"
#         ]
#         Resource = ["${aws_cloudwatch_log_group.api.arn}:*"]
#       }
#     ]
#   })
# }

# resource "aws_iam_role_policy_attachment" "ecs_task_deployer" {
#   role       = var.deployer_role_name == "my-role-name" ? null : "${var.deployer_role_name}"
#   policy_arn = aws_iam_policy.ecs_task_deletion_custom.arn
# }

resource "aws_iam_role_policy" "ecs_task_custom" {
  name = "${var.project_name}-${local.environment}-ecs-task-custom"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [aws_kms_key.cmk.arn]
      }
    ]
  })
}
resource "aws_iam_role_policy" "ecs_task_dynamodb" {
  name = "${var.project_name}-${local.environment}-ecs-task-dynamodb"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          "arn:aws:dynamodb:*:${local.account_id}:table/chats*",
          "arn:aws:dynamodb:*:${local.account_id}:table/documents*",
          "arn:aws:dynamodb:*:${local.account_id}:table/messages*",
          "arn:aws:dynamodb:*:${local.account_id}:table/streams*",
          "arn:aws:dynamodb:*:${local.account_id}:table/suggestions*",
          "arn:aws:dynamodb:*:${local.account_id}:table/test-scripts*",
          "arn:aws:dynamodb:*:${local.account_id}:table/users*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_s3_artifacts" {
  name = "${var.project_name}-ecs-task-s3-artifacts"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetObjectVersion",
          "s3:PutObjectAcl",
          "s3:GetObjectAcl"
        ]
        Resource = [
          aws_s3_bucket.artifacts.arn,
          "${aws_s3_bucket.artifacts.arn}/*"
        ]
      }
    ]
  })
} 