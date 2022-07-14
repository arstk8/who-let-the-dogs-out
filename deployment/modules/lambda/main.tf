variable s3_bucket {
  description = "The s3 bucket that contains the source code of the lambda"
  type        = string
}

variable s3_key {
  description = "The s3 key of the file that contains the source code of the lambda"
  type        = string
}

variable function_name {
  description = "The name of the lambda function"
  type        = string
}

variable handler {
  description = "The handler function in the source code"
  type        = string
}

variable runtime {
  description = "The lambda runtime to use"
  type        = string
}

variable role_name {
  description = "The name of the lambda's execution role"
  type        = string
}

variable policy_name {
  description = "The name of the principal of the lambda's execution role"
  type        = string
  default     = null
}

variable policy_json {
  description = "Json representation of the principal policy of the lambda's execution role"
  type        = string
  default     = null
}

variable environment {
  description = "The environment variables"
  type        = map(string)
  default     = {}
}

resource aws_lambda_function function {
  s3_bucket        = var.s3_bucket
  s3_key           = var.s3_key
  function_name    = var.function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = var.handler
  source_code_hash = filebase64sha256(var.s3_key)

  runtime = var.runtime

  environment {
    variables = var.environment
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_role_policy_attachment
  ]
}

output function_name {
  value = var.function_name
}

output invoke_arn {
  value = aws_lambda_function.function.invoke_arn
}