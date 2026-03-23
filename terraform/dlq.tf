# ── Dead Letter Queue ─────────────────────────────────────────────────
resource "aws_sqs_queue" "handler_dlq" {
  name                      = "address-validation-handler-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days
}

# ── IAM: Allow Lambda to send to DLQ ─────────────────────────────────
data "aws_iam_policy_document" "dlq_send" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.handler_dlq.arn]
  }
}

resource "aws_iam_role_policy" "dlq_send" {
  name   = "dlq-send"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.dlq_send.json
}

# ── CloudWatch Alarm: DLQ depth > 0 ──────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "dlq_depth" {
  alarm_name          = "address-validation-dlq-depth-${var.environment}"
  alarm_description   = "Messages in the handler dead letter queue"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.handler_dlq.name
  }

  alarm_actions = local.alarm_actions
  ok_actions    = local.alarm_actions
}
