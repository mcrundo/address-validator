# ── Handler Lambda ─────────────────────────────────────────────────────
resource "aws_lambda_function" "handler" {
  function_name = "address-validation-handler-${var.environment}"
  role          = aws_iam_role.lambda_exec.arn
  runtime       = "python3.12"
  handler       = "address_validation.handler.handler"
  timeout       = 30
  memory_size   = 256

  filename         = "${path.module}/../lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/../lambda.zip")

  environment {
    variables = {
      GOOGLE_MAPS_API_KEY = "" # Set after deploy via Secrets Manager
      LOG_LEVEL           = "INFO"
    }
  }

  lifecycle {
    ignore_changes = [environment]
  }

  depends_on = [aws_cloudwatch_log_group.handler]
}

resource "aws_cloudwatch_log_group" "handler" {
  name              = "/aws/lambda/address-validation-handler-${var.environment}"
  retention_in_days = 14
}

resource "aws_lambda_permission" "api_gateway_handler" {
  statement_id  = "AllowAPIGatewayInvokeHandler"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*"
}
