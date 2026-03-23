variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-2"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarm notifications (leave empty to skip SNS)"
  type        = string
  default     = ""
}
