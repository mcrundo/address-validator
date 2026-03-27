# ── HTTP API ───────────────────────────────────────────────────────────
resource "aws_apigatewayv2_api" "this" {
  name          = "address-validation-${var.environment}"
  protocol_type = "HTTP"
}

# ── Lambda Integration ────────────────────────────────────────────────
resource "aws_apigatewayv2_integration" "handler" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.handler.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# ── Route ─────────────────────────────────────────────────────────────
resource "aws_apigatewayv2_route" "validate" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "POST /v1/validate"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"

  authorization_type = "CUSTOM"
  authorizer_id      = aws_apigatewayv2_authorizer.api_key.id
}

# ── Health Integration ─────────────────────────────────────────────────
resource "aws_apigatewayv2_integration" "health" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.health.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "GET /v1/health"
  target    = "integrations/${aws_apigatewayv2_integration.health.id}"
}

# ── Stage ─────────────────────────────────────────────────────────────
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      errorMessage   = "$context.error.message"
    })
  }
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/address-validation-${var.environment}"
  retention_in_days = 14
}
