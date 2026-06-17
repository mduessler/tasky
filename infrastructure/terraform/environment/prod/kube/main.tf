data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.owner_id}-${var.environment}"
    key    = "network/terraform.tfstate"
    region = var.aws_region
  }
}


module "kubes" {
  for_each = var.workers_by_availability_zone

  source = "./modules/nodes"

  environment   = var.environment
  owner_id      = var.owner_id
  aws_region    = var.aws_region
  instance_type = each.value.instance_type
  vpc_id        = data.terraform_remote_state.network.outputs.ids[each.key]
  workers       = each.value.nodes
  clustername   = var.clustername
}

module "db_volumes" {
  for_each = var.workers_by_availability_zone

  source            = "./modules/db-volumes"
  availability_zone = each.key
  size              = each.value.size
  name              = each.value.name
}

module "aws_lb_nginx" {
  for_each = var.workers_by_availability_zone
  source   = "./modules/loadbalancer"

  vpc_id        = data.terraform_remote_state.network.outputs.ids[each.key]
  public_subnet = data.terraform_remote_state.network.outputs.public_subnets[data.terraform_remote_state.network.outputs.ids[each.key]]
  workers       = module.kubes[each.key].workers
}
