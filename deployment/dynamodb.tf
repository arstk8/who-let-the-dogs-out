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
  hash_key   = "owner_id"
  attributes = {
    owner_id = {
      name = "owner_id"
      type = "S"
    }
  }
  ttl = "ttl"
}

module owners_table {
  source        = "./modules/dynamodb"
  name          = "wltdo-owners"
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
  hash_key   = "owner_id"
  range_key  = "neighbor_group_id"
  attributes = {
    owner_id = {
      name = "owner_id"
      type = "S"
    }
    neighbor_group_id = {
      name = "neighbor_group_id"
      type = "S"
    }
  }
}
