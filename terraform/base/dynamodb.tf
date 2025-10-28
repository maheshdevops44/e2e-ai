# DynamoDB Table
resource "aws_dynamodb_table" "main" {
  name           = "${var.project_name}-${local.env}-table"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "id"
  
  # Only set capacity if using PROVISIONED billing mode
  read_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
  write_capacity = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null

  attribute {
    name = "id"
    type = "S"
  }

  # Optional GSI example - uncomment if needed
  # global_secondary_index {
  #   name            = "gsi1"
  #   hash_key        = "gsi1pk"
  #   range_key       = "gsi1sk"
  #   projection_type = "ALL"
  #   
  #   read_capacity  = null
  #   write_capacity = null
  # }

  # attribute {
  #   name = "gsi1pk"
  #   type = "S"
  # }

  # attribute {
  #   name = "gsi1sk"
  #   type = "S"
  # }

  # Enable encryption at rest using customer managed KMS key
  server_side_encryption {
    enabled = true
  }

  # Enable point in time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Enable deletion protection for production
  deletion_protection_enabled = local.env == "prod" ? true : false

  tags = merge(var.cigna_tags, {
    Name = "${var.project_name}-${local.env}-table"
    Environment = local.env
  })
}

# IAM policy for DynamoDB access
data "aws_iam_policy_document" "dynamodb_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:CreateTable",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem"
    ]
    resources = [
      aws_dynamodb_table.main.arn,
      "${aws_dynamodb_table.main.arn}/index/*",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/users",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/chats",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/documents",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/messages",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/streams",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/suggestions",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/test-scripts",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/users"
    ]
  }
}

resource "aws_iam_policy" "dynamodb_policy" {
  name        = "${var.project_name}-${local.env}-dynamodb-policy"
  description = "IAM policy for DynamoDB access"
  policy      = data.aws_iam_policy_document.dynamodb_policy.json
  tags        = var.cigna_tags
}

# Attach DynamoDB policy to ECS task role
resource "aws_iam_role_policy_attachment" "ecs_task_dynamodb" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
} 