data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.account_id}-${var.environment}"
    key    = "network/terraform.tfstate"
    region = var.backend_location
  }
}


module "kubes" {
  for_each = var.workers_by_availability_zone

  source = "./modules/nodes"

  environment   = var.environment
  account_id      = var.account_id
  backend_location    = var.backend_location
  instance_type = each.value.instance_type
  vpc_id        = data.terraform_remote_state.network.outputs.ids[each.key]
  workers       = each.value.nodes
  clustername   = var.clustername
}

module "db_volumes" {
  for_each = var.workers_by_availability_zone

  source            = "./modules/db-volumes"
  availability_zone = each.key
  sizes              = each.value.db_volumes.sizes
  names              = each.value.db_volumes.names
}

module "aws_lb_nginx" {
  for_each = var.workers_by_availability_zone
  source   = "./modules/loadbalancer"

  vpc_id        = data.terraform_remote_state.network.outputs.ids[each.key]
  public_subnet_id = data.terraform_remote_state.network.outputs.public_subnets[data.terraform_remote_state.network.outputs.ids[each.key]]
  workers       = module.kubes[each.key].workers
}
