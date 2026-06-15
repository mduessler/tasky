data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.owner_id}-${var.environment}"
    key    = "network/terraform.tfstate"
    region = var.aws_region
  }
}

module "iam" {
  source = "./modules/iam"
}

module "controller" {
  for_each             = data.terraform_remote_state.network.output.ids

  source               = "../../../modules/compute"
  ami_owners           = ["self"]
  ami_filter_values    = ["kube-node-*"]
  instance_type        = var.instance_type
  subnet_id            = data.terraform_remote_state.network.output.private_subnets[each.value]
  security_groups      = [data.terraform_remote_state.network.output.controller_sgs[each.value]]
  iam_instance_profile = module.iam.controller_profile_name
  http_hops            = 2
  root_volume_size     = 20
  tags = {
    Name                                       = "kube-controller"
    "kubernetes.io/cluster/${var.clustername}" = "owned"

  }
}

module "worker" {
  for_each = var.workers

  source               = "../../../modules/compute"
  ami_owners           = ["self"]
  ami_filter_values    = ["kube-node-*"]
  instance_type        = var.instance_type
  subnet_id            = module.network.private_subnet
  security_groups      = [aws_security_group.worker.id]
  iam_instance_profile = module.iam.worker_profile_name
  http_hops            = 2
  root_volume_size     = 50
  tags = {
    Name                                       = "kube-worker-${each.value}"
    "kubernetes.io/cluster/${var.clustername}" = "owned"
  }
}

resource "aws_ebs_volume" "postgres" {
  availability_zone = module.worker["01"].availability_zone
  size              = 10
  type              = "gp3"
  tags = {
    Name = "postgres-data"
  }
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
