resource "aws_iam_role" "mwaa_bq_oidc" {
  name = var.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "airflow.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::293661646409:oidc-provider/sts.amazonaws.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "sts.amazonaws.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}
