variable "role_name" {
  description = "Name for the MWAA OIDC IAM role."
  type        = string
  default     = "mwaa-oidc-role"
}

variable "oidc_provider_arns" {
  description = "List of OIDC provider ARNs to allow federated access (such as GCP Workload Identity Federation and others)."
  type        = list(string)
  default     = ["arn:aws:iam::293661646409:oidc-provider/sts.amazonaws.com"]
}

variable "oidc_conditions" {
  description = "Map of additional conditions for each OIDC provider. Keys should match the order/index of oidc_provider_arns. Values are condition blocks. Example: { 0 = { StringEquals = { 'sts.amazonaws.com:aud' = 'sts.amazonaws.com' } } }"
  type        = map(any)
  default     = { "0" = { StringEquals = { "sts.amazonaws.com:aud" = "sts.amazonaws.com" } } }
}
