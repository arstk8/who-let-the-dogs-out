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
}

resource aws_apigatewayv2_stage stage {
  api_id      = aws_apigatewayv2_api.api.id
  name        = var.stage_name
  auto_deploy = true

  default_route_settings {
    logging_level            = "INFO"
    detailed_metrics_enabled = true
    throttling_rate_limit = 10000
    throttling_burst_limit = 5000
  }
}

output api_endpoint {
  value = "${aws_apigatewayv2_api.api.api_endpoint}/${aws_apigatewayv2_stage.stage.name}"
}

output execution_arn {
  value = aws_apigatewayv2_api.api.execution_arn
}
