# ── SNS Topic (optional) ──────────────────────────────────────────────
resource "aws_sns_topic" "alarms" {
  count = var.alarm_email != "" ? 1 : 0
  name  = "address-validation-alarms-${var.environment}"
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alarm_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alarms[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

locals {
  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alarms[0].arn] : []
}

# ── Handler Error Rate ────────────────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "handler_errors" {
  alarm_name          = "address-validation-handler-errors-${var.environment}"
  alarm_description   = "Handler Lambda error count > 3 in 5 minutes"
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 3
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.handler.function_name
  }

  alarm_actions = local.alarm_actions
  ok_actions    = local.alarm_actions
}

# ── Handler Latency (p99) ─────────────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "handler_duration" {
  alarm_name          = "address-validation-handler-duration-${var.environment}"
  alarm_description   = "Handler Lambda p99 duration > 5 seconds"
  namespace           = "AWS/Lambda"
  metric_name         = "Duration"
  extended_statistic  = "p99"
  period              = 300
  evaluation_periods  = 1
  threshold           = 5000
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.handler.function_name
  }

  alarm_actions = local.alarm_actions
  ok_actions    = local.alarm_actions
}

# ── Handler Throttles ─────────────────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "handler_throttles" {
  alarm_name          = "address-validation-handler-throttles-${var.environment}"
  alarm_description   = "Handler Lambda is being throttled"
  namespace           = "AWS/Lambda"
  metric_name         = "Throttles"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.handler.function_name
  }

  alarm_actions = local.alarm_actions
  ok_actions    = local.alarm_actions
}

# ── Authorizer Error Rate ─────────────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "authorizer_errors" {
  alarm_name          = "address-validation-authorizer-errors-${var.environment}"
  alarm_description   = "Authorizer Lambda error count > 3 in 5 minutes"
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 3
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.authorizer.function_name
  }

  alarm_actions = local.alarm_actions
  ok_actions    = local.alarm_actions
}
