data aws_caller_identity current {}

data aws_region current {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
  aws_region     = data.aws_region.current.name
}

variable api {
  description = "The api details"
  type        = object({
    id    = string
    stage = string
  })
}

variable lambda_function_name {
  description = "The name of the lambda"
  type        = string
}

variable invoke_arn {
  description = "The invoke arn of the lambda"
  type        = string
}

variable route_key {
  description = "The route key"
  type        = string
}

resource aws_apigatewayv2_integration integration {
  api_id           = var.api.id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  content_handling_strategy = "CONVERT_TO_TEXT"
  integration_method        = "POST"
  integration_uri           = var.invoke_arn
  passthrough_behavior      = "WHEN_NO_MATCH"
}

resource aws_apigatewayv2_route route {
  api_id    = var.api.id
  route_key = var.route_key

  target = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource aws_lambda_permission lambda_permission {
  statement_id   = "AllowExecutionFromAPIGateway"
  action         = "lambda:InvokeFunction"
  function_name  = var.lambda_function_name
  principal      = "apigateway.amazonaws.com"
  source_account = local.aws_account_id
  source_arn     = "arn:aws:execute-api:${local.aws_region}:${local.aws_account_id}:${var.api.id}/${var.api.stage}/${var.route_key}"
}
