data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.account_id}-${var.environment}"
    key    = "network/terraform.tfstate"
    region = var.backend_location
  }
}


module "kubes" {
  for_each = var.workers_by_availability_zones

  source = "./modules/nodes"

  backend_location         = var.backend_location
  environment              = var.environment
  account_id               = var.account_id
  availability_zone        = each.key
  vpc_id                   = data.terraform_remote_state.network.outputs.ids[each.key]
  controller_instance_type = each.value.controller_instance_type
  worker_instance_type     = each.value.worker_instance_type
  workers                  = each.value.nodes
  clustername              = var.clustername
}

module "postgres_volumes" {
  for_each = var.workers_by_availability_zones

  source            = "./modules/block_volumes"
  availability_zone = each.key
  prefix            = "postgres"
  sizes             = each.value.postgres_volumes.sizes
  names             = each.value.postgres_volumes.names
}

module "etcd_volumes" {
  for_each = var.workers_by_availability_zones

  source            = "./modules/block_volumes"
  availability_zone = each.key
  prefix            = "etcd"
  sizes             = each.value.etcd_volumes.sizes
  names             = each.value.etcd_volumes.names
}

module "aws_lb_nginx" {
  for_each = var.workers_by_availability_zones
  source   = "./modules/loadbalancer"

  vpc_id        = data.terraform_remote_state.network.outputs.ids[each.key]
  public_subnet_id = data.terraform_remote_state.network.outputs.public_subnets[data.terraform_remote_state.network.outputs.ids[each.key]]
  workers       = module.kubes[each.key].workers
}
