# ── Google Maps API Key ────────────────────────────────────────────────
resource "aws_secretsmanager_secret" "google_maps_api_key" {
  name        = "address-validation/${var.environment}/google-maps-api-key"
  description = "Google Maps Address Validation API key"
}

# The secret value is set out-of-band. The handler Lambda fetches it at
# runtime via the AWS Secrets Manager API:
#   aws secretsmanager put-secret-value \
#     --secret-id address-validation/dev/google-maps-api-key \
#     --secret-string "<your-google-maps-api-key>" \
#     --region us-east-2 --profile aws

data "aws_iam_policy_document" "secrets_read" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.google_maps_api_key.arn]
  }
}

resource "aws_iam_role_policy" "secrets_read" {
  name   = "secrets-read"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.secrets_read.json
}
