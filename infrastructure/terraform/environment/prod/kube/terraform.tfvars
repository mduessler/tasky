workers_by_availability_zones = {
  "eu-central-1a" = {
    controller_instance_type = "t3.medium"
    worker_instance_type     = "t3.micro"
    nodes                    = ["node-a1", "node-a2"]
    postgres_volumes = {
      sizes = [10]
      names = ["01"]
    }
    etcd_volumes = {
      sizes = [10]
      names = ["01"]
    }
  }
  "eu-central-1b" = {
    controller_instance_type = "t3.medium"
    worker_instance_type     = "t3.micro"
    nodes                    = ["node-b1"]
    postgres_volumes = {
      sizes = [10]
      names = ["01"]
    }
    etcd_volumes = {
      sizes = [10]
      names = ["01"]
    }
  }
}
