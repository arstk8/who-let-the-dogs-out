variable name {
  description = "Name of the DynamoDB table"
  type        = string
}

variable billing_mode {
  description = "The billing mode"
  default     = "PROVISIONED"
  type        = string
}

variable read_capacity {
  description = "The read capacity"
  type        = object({
    capacity                   = number
    min_capacity               = number
    max_capacity               = number
    target_capacity_percentage = number
  })
}

variable write_capacity {
  description = "The write capacity"
  type        = object({
    capacity                   = number
    min_capacity               = number
    max_capacity               = number
    target_capacity_percentage = number
  })
}

variable hash_key {
  description = "The hash key"
  type        = string
}

variable range_key {
  description = "The range key"
  type        = string
  default     = null
}

variable attributes {
  description = "The attributes of the table"
  type        = map(object({
    name = string
    type = string
  }))
  default = null
}

variable ttl {
  description = "The TTL attribute"
  type        = string
  default     = null
}

resource aws_dynamodb_table table {
  name           = var.name
  billing_mode   = var.billing_mode
  read_capacity  = var.read_capacity.capacity
  write_capacity = var.write_capacity.capacity
  hash_key       = var.hash_key
  range_key      = var.range_key

  dynamic attribute {
    for_each = var.attributes

    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  dynamic ttl  {
    for_each = var.ttl == null ? [] : [var.ttl]

    content {
      attribute_name = ttl.value
      enabled        = true
    }
  }
}

resource aws_appautoscaling_target table_read_target {
  max_capacity       = var.read_capacity.max_capacity
  min_capacity       = var.read_capacity.min_capacity
  resource_id        = "table/${aws_dynamodb_table.table.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource aws_appautoscaling_policy table_read_policy {
  name               = "dynamodb-read-capacity-utilization-${aws_appautoscaling_target.table_read_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.table_read_target.resource_id
  scalable_dimension = aws_appautoscaling_target.table_read_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.table_read_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = var.read_capacity.target_capacity_percentage
  }
}

resource aws_appautoscaling_target table_write_target {
  max_capacity       = var.write_capacity.max_capacity
  min_capacity       = var.write_capacity.min_capacity
  resource_id        = "table/${aws_dynamodb_table.table.name}"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource aws_appautoscaling_policy table_write_policy {
  name               = "dynamodb-write-capacity-utilization-${aws_appautoscaling_target.table_write_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.table_write_target.resource_id
  scalable_dimension = aws_appautoscaling_target.table_write_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.table_write_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
    target_value = var.write_capacity.target_capacity_percentage
  }
}

output arn {
  value = aws_dynamodb_table.table.arn
}

output name {
  value = aws_dynamodb_table.table.name
}
