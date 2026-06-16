workers_by_availability_zone = {
  "eu-central-1a" = {
    instance_type = "node-group-a"
    nodes         = ["node-a1", "node-a2"]
  }
  "eu-central-1b" = {
    name  = "node-group-b"
    nodes = ["node-b1"]
    db_volumes = [
      {
        size = 10,
        name = "01"
      }
    ]
  }
}
