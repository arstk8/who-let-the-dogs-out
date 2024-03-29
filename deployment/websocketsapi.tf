module websocket_api {
  source = "./modules/websocketapi"

  name   = "WhoLetTheDogsOut"
  routes = {
    connect_route = {
      route_key            = "$connect"
      lambda_function_name = module.connect_lambda.function_name
      invoke_arn           = module.connect_lambda.invoke_arn
    }
    disconnect_route = {
      route_key            = "$disconnect"
      lambda_function_name = module.disconnect_lambda.function_name
      invoke_arn           = module.disconnect_lambda.invoke_arn
    }
    status_route = {
      route_key            = "status"
      lambda_function_name = module.status_lambda.function_name
      invoke_arn           = module.status_lambda.invoke_arn
    }
    neighbors_route = {
      route_key            = "neighbors"
      lambda_function_name = module.neighbors_lambda.function_name
      invoke_arn           = module.neighbors_lambda.invoke_arn
    }
    release_route = {
      route_key            = "release"
      lambda_function_name = module.release_lambda.function_name
      invoke_arn           = module.release_lambda.invoke_arn
    },
    unrelease_route = {
      route_key            = "unrelease"
      lambda_function_name = module.unrelease_lambda.function_name
      invoke_arn           = module.unrelease_lambda.invoke_arn
    }
  }
  authorizer_lambda = {
    name       = module.authorizer_lambda.function_name
    invoke_arn = module.authorizer_lambda.invoke_arn
  }
}