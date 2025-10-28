# Generate a random 32-character base64 string for AUTH_SECRET
# This is used by NextAuth.js for JWT token signing and encryption
resource "random_password" "auth_secret" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# Store the AUTH_SECRET in AWS Secrets Manager for secure access
resource "aws_secretsmanager_secret" "auth_secret" {
  name                    = "${var.project_name}-${local.environment}-auth-secret"
  description             = "AUTH_SECRET for NextAuth.js authentication"
  recovery_window_in_days = 0 # Allows immediate deletion for non-prod environments

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-auth-secret"
    Environment = local.environment
  })
}

resource "aws_secretsmanager_secret_version" "auth_secret" {
  secret_id     = aws_secretsmanager_secret.auth_secret.id
  secret_string = base64encode(random_password.auth_secret.result)
}
