module connections_table {
  source        = "./modules/dynamodb"
  name          = "wltdo-connections"
  billing_mode  = "PROVISIONED"
  read_capacity = {
    capacity                   = 1
    min_capacity               = 1
    max_capacity               = 10
    target_capacity_percentage = 70
  }
  write_capacity = {
    capacity                   = 1
    min_capacity               = 1
    max_capacity               = 10
    target_capacity_percentage = 70
  }
  hash_key   = "connection_id"
  attributes = {
    connection_id = {
      name = "connection_id"
      type = "S"
    }
  }
  ttl = "ttl"
}

module hounds_table {
  source        = "./modules/dynamodb"
  name          = "wltdo-hounds-out"
  billing_mode  = "PROVISIONED"
  read_capacity = {
    capacity                   = 1
    min_capacity               = 1
    max_capacity               = 10
    target_capacity_percentage = 70
  }
  write_capacity = {
    capacity                   = 1
    min_capacity               = 1
    max_capacity               = 10
    target_capacity_percentage = 70
  }
  hash_key   = "neighbor_group"
  range_key  = "username"
  attributes = {
    neighbor_group = {
      name = "neighbor_group"
      type = "S"
    }
    username = {
      name = "username"
      type = "S"
    }
  }
  ttl = "ttl"
}

module users_table {
  source        = "./modules/dynamodb"
  name          = "wltdo-users"
  billing_mode  = "PROVISIONED"
  read_capacity = {
    capacity                   = 1
    min_capacity               = 1
    max_capacity               = 10
    target_capacity_percentage = 70
  }
  write_capacity = {
    capacity                   = 1
    min_capacity               = 1
    max_capacity               = 10
    target_capacity_percentage = 70
  }
  hash_key   = "neighbor_group"
  range_key  = "username"
  attributes = {
    neighbor_group = {
      name = "neighbor_group"
      type = "S"
    }
    username = {
      name = "username"
      type = "S"
    }
  }
}
