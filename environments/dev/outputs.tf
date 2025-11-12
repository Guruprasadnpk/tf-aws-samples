output "mwaa_webserver_url" {
  description = "The webserver URL of the MWAA Environment"
  value       = module.mwaa.mwaa_webserver_url
}

output "mwaa_arn" {
  description = "The ARN of the MWAA Environment"
  value       = module.mwaa.mwaa_arn
}

output "mwaa_service_role_arn" {
  description = "The Service Role ARN of the Amazon MWAA Environment"
  value       = module.mwaa.mwaa_service_role_arn
}

output "mwaa_status" {
  description = " The status of the Amazon MWAA Environment"
  value       = module.mwaa.mwaa_status
}

output "mwaa_role_arn" {
  description = "The ARN of the MWAA Environment"
  value       = module.mwaa.mwaa_role_arn
}

output "mwaa_security_group_id" {
  description = "The ARN of the MWAA Environment"
  value       = module.mwaa.mwaa_security_group_id
}

# PostgreSQL DB outputs for test/demo
data "aws_db_instance" "pg" {
  db_instance_identifier = aws_db_instance.pg.id
}

output "pg_db_address" {
  value = data.aws_db_instance.pg.address
}
output "pg_db_port" {
  value = data.aws_db_instance.pg.port
}
output "pg_db_name" {
  value = aws_db_instance.pg.db_name
}
output "pg_db_username" {
  value = aws_db_instance.pg.username
}
output "pg_db_password" {
  value     = aws_db_instance.pg.password
  sensitive = true
}
output "pg_db_security_group_id" {
  value = aws_security_group.pg.id
}
