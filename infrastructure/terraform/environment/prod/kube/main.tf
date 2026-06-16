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

  source = "./modules/db-volumes"
  availability_zone = each.key
  size = each.value.size
  name = each.value.name
}

resource "aws_lb" "nginx" {
  name               = "nginx-nlb"
  load_balancer_type = "network"
  subnets            = [module.network.public_subnet]
}

resource "aws_lb_target_group" "nginx" {
  name     = "nginx-tg"
  port     = 30443
  protocol = "TCP"
  vpc_id   = module.network.vpc_id
}

resource "aws_lb_listener" "nginx" {
  load_balancer_arn = aws_lb.nginx.arn
  port              = 443
  protocol          = "TCP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.nginx.arn
  }
}

resource "aws_lb_target_group_attachment" "nginx" {
  for_each         = var.workers
  target_group_arn = aws_lb_target_group.nginx.arn
  target_id        = module.worker[each.key].id
  port             = 30443
}
