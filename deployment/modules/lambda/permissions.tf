data aws_iam_policy_document lambda_assume_role_policy_document {
  statement {
    effect = "Allow"
    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
    actions = ["sts:AssumeRole"]
  }
}

resource aws_iam_role lambda_role {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy_document.json
}

resource aws_iam_role_policy_attachment role_attachment {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource aws_iam_policy lambda_policy {
  count  = var.policy_name == null ? 0 : 1
  name   = var.policy_name
  policy = var.policy_json
}

resource aws_iam_role_policy_attachment lambda_role_policy_attachment {
  count      = var.policy_name == null ? 0 : 1
  policy_arn = aws_iam_policy.lambda_policy[0].arn
  role       = aws_iam_role.lambda_role.name
}
