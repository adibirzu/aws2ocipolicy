import json

aws_to_oci_action_map = {
    "describe": "inspect", "get": "inspect", "list": "inspect",
    "read": "read", "create": "use", "delete": "manage",
    "update": "use", "put": "use", "post": "use",
    "attach": "use", "detach": "manage", "modify": "manage",
    "start": "use", "stop": "use", "terminate": "manage",
}

aws_service_to_oci_resources = {
    "ec2": "instances", "s3": "object-family",
    "iam": "identity-resources", "apigateway": "api-gateways",
    "lambda": "functions", "dynamodb": "nosql-tables",
    "rds": "db-systems", "cloudwatch": "metrics",
    "cloudtrail": "audit-events", "secretsmanager": "vault-secrets",
    "kms": "keys",
}

oci_condition_variables = {
    "aws:SourceIp": "request.networkSource.name",
    "aws:username": "request.user.name",
    "aws:userid": "request.user.id",
    "aws:PrincipalOrgID": "request.user.compartment.id",
    "aws:RequestedRegion": "request.region",
    "aws:SecureTransport": "request.authScheme",
}

aws_condition_operator_mapping = {
    "StringEquals": "==",
    "StringNotEquals": "!=",
    "StringLike": "=~",
    "NumericEquals": "==",
    "NumericLessThan": "<",
    "NumericGreaterThan": ">",
    "DateGreaterThan": ">",
    "DateLessThan": "<",
    "Bool": "==",
    "IpAddress": "==",
    "NotIpAddress": "!=",
}

def aws_action_to_oci(action):
    service, operation = action.lower().split(":")
    for key, verb in aws_to_oci_action_map.items():
        if operation.startswith(key):
            resource = aws_service_to_oci_resources.get(service, "all-resources")
            return verb, resource
    return "use", aws_service_to_oci_resources.get(service, "all-resources")

def parse_aws_conditions_to_oci(conditions):
    oci_conditions = []

    for aws_operator, condition_content in conditions.items():
        oci_operator = aws_condition_operator_mapping.get(aws_operator)
        if not oci_operator:
            continue  # Skip unsupported operators

        for aws_key, value in condition_content.items():
            oci_var = oci_condition_variables.get(aws_key, aws_key)

            # Special handling for SecureTransport → request.authScheme
            if aws_key == "aws:SecureTransport":
                value = "tls" if value.lower() == "true" else "none"

            # IP Address handling
            if aws_operator in ["IpAddress", "NotIpAddress"]:
                condition = f"{oci_var} {oci_operator} '{value}'"
            elif aws_operator == "Bool":
                value = "true" if str(value).lower() == "true" else "false"
                condition = f"{oci_var} {oci_operator} {value}"
            else:
                condition = f"{oci_var} {oci_operator} '{value}'"

            oci_conditions.append(condition)

    return " and ".join(oci_conditions) if oci_conditions else None

def translate_aws_to_oci(aws_policy_json, oci_group_name="ImportedAWSGroup"):
    aws_policy = json.loads(aws_policy_json)
    oci_policy_statements = set()

    for stmt in aws_policy.get("Statement", []):
        actions = stmt["Action"]
        conditions = stmt.get("Condition", {})
        oci_conditions = parse_aws_conditions_to_oci(conditions)

        if isinstance(actions, str):
            actions = [actions]

        for action in actions:
            verb, resource = aws_action_to_oci(action)
            oci_policy = f"Allow group {oci_group_name} to {verb} {resource} in tenancy"
            if oci_conditions:
                oci_policy += f" where {oci_conditions}"
            oci_policy_statements.add(oci_policy)

    return "\n".join(sorted(oci_policy_statements))
