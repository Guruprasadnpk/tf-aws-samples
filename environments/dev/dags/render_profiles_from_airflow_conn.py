import os
import re
import subprocess

# Set parameters for AWS
secret_id = "airflow/connections/my_postgres_db"
aws_region = os.environ.get("AWS_REGION", "us-east-1")

# Fetch the URI from AWS Secrets Manager
cmd = [
    "aws", "secretsmanager", "get-secret-value",
    "--region", aws_region,
    "--secret-id", secret_id,
    "--query", "SecretString",
    "--output", "text"
]
connection_uri = subprocess.check_output(cmd, text=True).strip()

# Example: postgresql://airflow:somepass@dbhost:5432/airflowdb
pattern = r"postgresql:\/\/(.*?):(.*?)@(.*?):(\d+)\/(.*)"
match = re.match(pattern, connection_uri)
if not match:
    raise Exception("Secret connection URI is not a valid PostgreSQL URI!")

user, password, host, port, dbname = match.groups()

# Write out dbt profiles.yml for this project
profiles_yml = f"""
default:
  target: dev
  outputs:
    dev:
      type: postgres
      threads: 1
      host: "{host}"
      user: "{user}"
      password: "{password}"
      port: {port}
      dbname: {dbname}
      schema: public
"""
with open("/tmp/profiles.yml", "w") as f:
    f.write(profiles_yml)

print("profiles.yml written to /tmp/profiles.yml")
