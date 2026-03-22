# ── API Key Secret ─────────────────────────────────────────────────────
resource "aws_secretsmanager_secret" "api_key" {
  name        = "address-validation/${var.environment}/api-key"
  description = "API key for authenticating requests to the address validation service"
}

# Value is set out-of-band:
#   aws secretsmanager put-secret-value \
#     --secret-id address-validation/dev/api-key \
#     --secret-string "$(openssl rand -hex 32)" \
#     --profile aws

# ── Authorizer Lambda ─────────────────────────────────────────────────
data "aws_iam_policy_document" "authorizer_secrets" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.api_key.arn]
  }
}

resource "aws_iam_role_policy" "authorizer_secrets" {
  name   = "authorizer-secrets-read"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.authorizer_secrets.json
}

resource "aws_lambda_function" "authorizer" {
  function_name = "address-validation-authorizer-${var.environment}"
  role          = aws_iam_role.lambda_exec.arn
  runtime       = "python3.12"
  handler       = "address_validation.authorizer.handler"
  timeout       = 5
  memory_size   = 128

  filename         = "${path.module}/../lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/../lambda.zip")

  environment {
    variables = {
      API_KEY   = "" # Populated at deploy time — see note below
      LOG_LEVEL = "INFO"
    }
  }

  # NOTE: In production, read from Secrets Manager at cold start instead of
  # passing via env var. For now, set the value after deploy:
  #   aws lambda update-function-configuration \
  #     --function-name address-validation-authorizer-dev \
  #     --environment "Variables={API_KEY=$(aws secretsmanager get-secret-value \
  #       --secret-id address-validation/dev/api-key \
  #       --query SecretString --output text --profile aws),LOG_LEVEL=INFO}" \
  #     --profile aws

  depends_on = [aws_cloudwatch_log_group.authorizer]
}

resource "aws_cloudwatch_log_group" "authorizer" {
  name              = "/aws/lambda/address-validation-authorizer-${var.environment}"
  retention_in_days = 14
}

# ── API Gateway Authorizer ────────────────────────────────────────────
resource "aws_apigatewayv2_authorizer" "api_key" {
  api_id           = aws_apigatewayv2_api.this.id
  authorizer_type  = "REQUEST"
  name             = "api-key-authorizer"
  identity_sources = ["$request.header.x-api-key"]

  authorizer_uri                    = aws_lambda_function.authorizer.invoke_arn
  authorizer_payload_format_version = "2.0"
  enable_simple_responses           = true

  # Cache for 5 minutes per unique API key value
  authorizer_result_ttl_in_seconds = 300
}

resource "aws_lambda_permission" "authorizer_invoke" {
  statement_id  = "AllowAPIGatewayInvokeAuthorizer"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.authorizer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*"
}
