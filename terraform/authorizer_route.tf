# Wire the authorizer to the POST /validate route.
#
# If your api_gateway.tf has an aws_apigatewayv2_route resource,
# add these two arguments to it instead of using this file:
#
#   authorization_type = "CUSTOM"
#   authorizer_id      = aws_apigatewayv2_authorizer.api_key.id
#
# This file exists as a reference — merge into your route resource after
# confirming the resource name from RUB-42.

# Example (uncomment and adjust resource name if needed):
# resource "aws_apigatewayv2_route" "validate" {
#   api_id    = aws_apigatewayv2_api.this.id
#   route_key = "POST /validate"
#   target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
#
#   authorization_type = "CUSTOM"
#   authorizer_id      = aws_apigatewayv2_authorizer.api_key.id
# }
