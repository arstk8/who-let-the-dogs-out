data aws_caller_identity current {}

data aws_region current {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
  aws_region     = data.aws_region.current.name
}

variable name {
  description = "The name of the API"
  type        = string
}

variable route_selection_expression {
  description = "The protocol type of the API"
  type        = string
  default     = "$request.body.action"
}

variable stage_name {
  description = "The name of the main stage"
  type        = string
  default     = "production"
}

variable routes {
  description = "The routes for this API"
  type        = map(
    object({
      route_key            = string
      lambda_function_name = string
      invoke_arn           = string
    })
  )
}

variable authorizer_lambda {
  description = "The authorizer lambda"
  type        = object({
    name       = string
    invoke_arn = string
  })
  default = null
}

resource aws_apigatewayv2_api api {
  name                       = var.name
  protocol_type              = "WEBSOCKET"
  route_selection_expression = var.route_selection_expression
}

module routes {
  for_each = var.routes
  source   = "./route"

  api = {
    id    = aws_apigatewayv2_api.api.id
    stage = var.stage_name
  }
  lambda_function_name = each.value.lambda_function_name
  invoke_arn           = each.value.invoke_arn
  route_key            = each.value.route_key
  authorizer_id        = aws_apigatewayv2_authorizer.authorizer[0].id
}

resource aws_apigatewayv2_stage stage {
  api_id      = aws_apigatewayv2_api.api.id
  name        = var.stage_name
  auto_deploy = true

  default_route_settings {
    logging_level            = "INFO"
    detailed_metrics_enabled = true
    throttling_rate_limit    = 10000
    throttling_burst_limit   = 5000
  }
}

resource aws_apigatewayv2_authorizer authorizer {
  count            = var.authorizer_lambda == null ? 0 : 1
  api_id           = aws_apigatewayv2_api.api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = var.authorizer_lambda.invoke_arn
  identity_sources = ["route.request.header.Authorization"]
  name             = "websockets-authorizer"
}

resource aws_lambda_permission lambda_permission {
  count          = var.authorizer_lambda == null ? 0 : 1
  statement_id   = "AllowExecutionFromAPIGateway"
  action         = "lambda:InvokeFunction"
  function_name  = var.authorizer_lambda.name
  principal      = "apigateway.amazonaws.com"
  source_account = local.aws_account_id
  source_arn     = "arn:aws:execute-api:${local.aws_region}:${local.aws_account_id}:${aws_apigatewayv2_api.api.id}/authorizers/${aws_apigatewayv2_authorizer.authorizer[0].id}"
}

output api_endpoint {
  value = "${aws_apigatewayv2_api.api.api_endpoint}/${aws_apigatewayv2_stage.stage.name}"
}

output execution_arn {
  value = aws_apigatewayv2_api.api.execution_arn
}
