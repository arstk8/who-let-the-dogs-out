locals {
  connect_function_name    = "wltdo-connect"
  disconnect_function_name = "wltdo-disconnect"
  status_function_name     = "wltdo-houndstatus"
  neighbors_function_name  = "wltdo-neighbors"
  release_function_name    = "wltdo-releasethehounds"
  unrelease_function_name  = "wltdo-letthehoundsin"
  authorizer_function_name = "wltdo-authorizer"
}

module connect_lambda {
  source        = "./modules/lambda"
  filename      = "dist.zip"
  function_name = local.connect_function_name
  handler       = "src/who_let_the_dogs_out/connect.handle"
  runtime       = "python3.8"
  role_name     = "wltdo-connection-role"
  policy_name   = "wltdo-connection-policy"
  policy_json   = data.aws_iam_policy_document.connection_policy_document.json
  environment   = {
    CONNECTION_TABLE_NAME = module.connections_table.name
    USERS_TABLE_NAME      = module.users_table.name
  }
}

data aws_iam_policy_document connection_policy_document {
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:PutItem"
    ]
    resources = [module.connections_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:PutItem"
    ]
    resources = [module.users_table.arn]
  }
}

module disconnect_lambda {
  source        = "./modules/lambda"
  filename      = "dist.zip"
  function_name = local.disconnect_function_name
  handler       = "src/who_let_the_dogs_out/disconnect.handle"
  runtime       = "python3.8"
  role_name     = "wltdo-disconnect-role"
  policy_name   = "wltdo-disconnect-policy"
  policy_json   = data.aws_iam_policy_document.disconnect_policy_document.json
  environment   = {
    CONNECTION_TABLE_NAME = module.connections_table.name
  }
}

data aws_iam_policy_document disconnect_policy_document {
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:DeleteItem"
    ]
    resources = [module.connections_table.arn]
  }
}

module status_lambda {
  source        = "./modules/lambda"
  filename      = "dist.zip"
  function_name = local.status_function_name
  handler       = "src/who_let_the_dogs_out/hound_status.handle"
  runtime       = "python3.8"
  role_name     = "wltdo-status-role"
  policy_name   = "wltdo-status-policy"
  policy_json   = data.aws_iam_policy_document.status_policy_document.json
  environment   = {
    CONNECTION_TABLE_NAME = module.connections_table.name
    DOG_TABLE_NAME        = module.hounds_table.name
    ENDPOINT_URL          = "${module.websocket_api.api_endpoint}/${module.websocket_api.stage}"
  }
}

data aws_iam_policy_document status_policy_document {
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:Query"
    ]
    resources = [module.hounds_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:Query"
    ]
    resources = [module.connections_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "execute-api:Invoke",
      "execute-api:ManageConnections"
    ]
    resources = ["${module.websocket_api.execution_arn}/*"]
  }
}

module neighbors_lambda {
  source        = "./modules/lambda"
  filename      = "dist.zip"
  function_name = local.neighbors_function_name
  handler       = "src/who_let_the_dogs_out/neighbors.handle"
  runtime       = "python3.8"
  role_name     = "wltdo-neighbors-role"
  policy_name   = "wltdo-neighbors-policy"
  policy_json   = data.aws_iam_policy_document.neighbors_policy_document.json
  environment   = {
    CONNECTION_TABLE_NAME = module.connections_table.name
    USERS_TABLE_NAME      = module.users_table.name
    ENDPOINT_URL          = "${module.websocket_api.api_endpoint}/${module.websocket_api.stage}"
  }
}

data aws_iam_policy_document neighbors_policy_document {
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:Query"
    ]
    resources = [module.users_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:Query"
    ]
    resources = [module.connections_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "execute-api:Invoke",
      "execute-api:ManageConnections"
    ]
    resources = ["${module.websocket_api.execution_arn}/*"]
  }
}

module release_lambda {
  source        = "./modules/lambda"
  filename      = "dist.zip"
  function_name = local.release_function_name
  handler       = "src/who_let_the_dogs_out/release_the_hounds.handle"
  runtime       = "python3.8"
  role_name     = "wltdo-release-role"
  policy_name   = "wltdo-release-policy"
  policy_json   = data.aws_iam_policy_document.release_policy_document.json
  environment   = {
    CONNECTION_TABLE_NAME = module.connections_table.name
    DOG_TABLE_NAME        = module.hounds_table.name
    ENDPOINT_URL          = "${module.websocket_api.api_endpoint}/${module.websocket_api.stage}"
  }
}

data aws_iam_policy_document release_policy_document {
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:PutItem"
    ]
    resources = [module.hounds_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:Scan",
      "dynamodb:Query"
    ]
    resources = [module.connections_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "execute-api:Invoke",
      "execute-api:ManageConnections"
    ]
    resources = ["${module.websocket_api.execution_arn}/*"]
  }
}

module unrelease_lambda {
  source        = "./modules/lambda"
  filename      = "dist.zip"
  function_name = local.unrelease_function_name
  handler       = "src/who_let_the_dogs_out/let_the_hounds_in.handle"
  runtime       = "python3.8"
  role_name     = "wltdo-unrelease-role"
  policy_name   = "wltdo-unrelease-policy"
  policy_json   = data.aws_iam_policy_document.unrelease_policy_document.json
  environment   = {
    CONNECTION_TABLE_NAME = module.connections_table.name
    DOG_TABLE_NAME        = module.hounds_table.name
    ENDPOINT_URL          = "${module.websocket_api.api_endpoint}/${module.websocket_api.stage}"
  }
}

data aws_iam_policy_document unrelease_policy_document {
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:DeleteItem"
    ]
    resources = [module.hounds_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:Scan",
      "dynamodb:Query"
    ]
    resources = [module.connections_table.arn]
  }
  statement {
    effect  = "Allow"
    actions = [
      "execute-api:Invoke",
      "execute-api:ManageConnections"
    ]
    resources = ["${module.websocket_api.execution_arn}/*"]
  }
}

module authorizer_lambda {
  source        = "./modules/lambda"
  filename      = "dist.zip"
  function_name = local.authorizer_function_name
  handler       = "src/who_let_the_dogs_out/authorizer.handle"
  runtime       = "python3.8"
  role_name     = "wltdo-authorizer-role"
  environment   = {
    CLOUDFRONT_SECRET = var.cloudfront_secret
  }
}