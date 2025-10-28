resource "aws_kms_key" "cmk" {
  description             = "The customer managed KMS key used to encrypt data at rest across the ${var.project_name} workload."
  policy = data.aws_iam_policy_document.cmk_resource_policy.json
  enable_key_rotation = true
  tags = var.cigna_tags
}

resource "aws_kms_alias" "cmk" {
  name          = "alias/${var.project_name}-${local.env}-key"
  target_key_id = aws_kms_key.cmk.id
}

data "aws_iam_policy_document" "cmk_resource_policy" {
  statement  {
    # Understand what this does: https://docs.aws.amazon.com/kms/latest/developerguide/key-policy-default.html
    sid = "DelegatesKeyUsageToIAM"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:Encrypt",
      "kms:DescribeKey",
      "kms:GenerateDataKey",
      "kms:ReEncrypt*"
    ]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${local.account_id}:root"]
    }
  }

  statement  {
    sid = "AdminDeployerPermissions"
    effect = "Allow"
    actions = [
      "kms:Create*",
      "kms:Describe*",
      "kms:Enable*",
      "kms:List*",
      "kms:Put*",
      "kms:Update*",
      "kms:Revoke*",
      "kms:Disable*",
      "kms:Get*",
      "kms:Delete*",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion"]
    resources = ["*"]
    principals {
      type        = "AWS"
      # This key policy statement allows the deployer role and ACCOUNTADMIN role full access (create/destroy/update) to the KMS key
      # This only gets added when the CICD steps in the README are completed and the var.deployer_role_name gets the correct IAM role name assigned
      identifiers = compact(concat(
        ["arn:aws:iam::${local.account_id}:role/${local.env == "dev" ? "ACCOUNTADMIN" : "OrganizationAccountAccessRole"}"],
        [var.deployer_role_name == "my-role-name" ? null : "arn:aws:iam::${local.account_id}:role/Enterprise/${var.deployer_role_name}"]
      ))
    }
  }

  statement {
    sid = "AllowCloudWatchLogs"
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = ["*"]
    principals {
      type        = "Service"
      identifiers = ["logs.${data.aws_region.current.name}.amazonaws.com"]
    }
    # condition {
    #   test     = "StringEquals"
    #   variable = "kms:EncryptionContext:aws:logs:arn"
    #   values   = [
    #     "arn:aws:logs:${data.aws_region.current.name}:${local.account_id}:log-group:${aws_cloudwatch_log_group.app.name}"
    #   ]
    # }
  }
}

output "kms_admin_role_identifiers" {
  description = "The role identifiers used in the KMS key policy for debugging"
  value = compact(concat(
    ["arn:aws:iam::${local.account_id}:role/${local.env == "dev" ? "ACCOUNTADMIN" : "OrganizationAccountAccessRole"}"],
    [var.deployer_role_name == "my-role-name" ? null : "arn:aws:iam::${local.account_id}:role/${var.deployer_role_name}"]
  ))
  sensitive = true
}