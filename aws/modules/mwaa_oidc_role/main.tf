resource "aws_iam_role" "mwaa_bq_oidc" {
  name = var.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Allow the MWAA execution role to assume this role.
      {
        Effect = "Allow"
        Principal = {
          AWS = var.mwaa_execution_role_arn
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}
