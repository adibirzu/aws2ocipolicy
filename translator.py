import json
import re

# AWS IAM to OCI Verb mapping (granular and accurate)
aws_to_oci_action_map = {
    "describe": "inspect",
    "get": "inspect",
    "list": "inspect",
    "read": "read",
    "create": "use",
    "delete": "manage",
    "update": "use",
    "put": "use",
    "post": "use",
    "attach": "use",
    "detach": "manage",
    "modify": "manage",
    "start": "use",
    "stop": "use",
    "terminate": "manage",
}

# Expanded AWS service → OCI resource mappings
aws_service_to_oci_resources = {
    "ec2": "instances",
    "s3": "object-family",
    "iam": "identity-resources",
    "apigateway": "api-gateways",
    "lambda": "functions",
    "dynamodb": "nosql-tables",
    "rds": "db-systems",
    "cloudwatch": "metrics",
    "cloudtrail": "audit-events",
    "secretsmanager": "vault-secrets",
    "kms": "keys",
    # Add more mappings based on your needs
}

def aws_action_to_oci(action):
    service, operation = action.lower().split(":")
    for key, verb in aws_to_oci_action_map.items():
        if operation.startswith(key):
            resource = aws_service_to_oci_resources.get(service, "all-resources")
            return verb, resource
    return "use", aws_service_to_oci_resources.get(service, "all-resources")

def parse_conditions(conditions):
    oci_conditions = []
    for condition_operator, condition_kv in conditions.items():
        for condition_key, condition_value in condition_kv.items():
            condition_str = f"{condition_key}='{condition_value}'"
            oci_conditions.append(condition_str)
    return " and ".join(oci_conditions)

def translate_aws_to_oci(aws_policy_json, oci_group_name="ImportedAWSGroup"):
    aws_policy = json.loads(aws_policy_json)
    oci_policy_statements = set()

    for stmt in aws_policy.get("Statement", []):
        actions = stmt["Action"]
        conditions = stmt.get("Condition", {})
        oci_conditions = parse_conditions(conditions) if conditions else None

        if isinstance(actions, str):
            actions = [actions]

        for action in actions:
            verb, resource = aws_action_to_oci(action)
            oci_policy = f"Allow group {oci_group_name} to {verb} {resource} in tenancy"
            if oci_conditions:
                oci_policy += f" where {oci_conditions}"
            oci_policy_statements.add(oci_policy)

    return "\n".join(sorted(oci_policy_statements))
