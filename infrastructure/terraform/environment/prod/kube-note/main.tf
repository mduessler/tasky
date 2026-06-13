module "network" {
  source     = "../../../modules/network"
  aws_region = var.aws_region
  private_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    "kubernetes.io/role/internal-elb"           = "1"
  }
  public_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    "kubernetes.io/role/elb"                    = "1"
  }
}

resource "aws_security_group" "controller" {
  name        = "kube-controller-sg"
  description = "Security Group for the controller of the kubernetes"
  vpc_id      = module.network.vpc

  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = [module.network.vpc_cidr]
  }

  ingress {
    from_port   = 2379
    to_port     = 2380
    protocol    = "tcp"
    cidr_blocks = [module.network.vpc_cidr]
  }

  ingress {
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    cidr_blocks = [module.network.vpc_cidr]
  }

  ingress {
    from_port   = 10257
    to_port     = 10257
    protocol    = "tcp"
    cidr_blocks = [module.network.vpc_cidr]
  }

  ingress {
    from_port   = 10259
    to_port     = 10259
    protocol    = "tcp"
    cidr_blocks = [module.network.vpc_cidr]
  }

  egress { # In a real secure environment, define the outgoing connections better.
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "worker" {
  name        = "kube-worker-sg"
  description = "Security Group for the workers of the kubernetes"
  vpc_id      = module.network.vpc

  ingress {
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    cidr_blocks = [module.network.vpc_cidr]
  }

  ingress {
    from_port   = 30443
    to_port     = 30443
    protocol    = "tcp"
    cidr_blocks = [module.network.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

module "iam" {
  source = "./modules/iam"
}

module "controller" {
  source               = "../../../modules/compute"
  ami_owners           = ["self"]
  ami_filter_values    = ["kube-node-*"]
  instance_type        = var.instance_type
  subnet_id            = module.network.private_subnet
  security_groups      = [aws_security_group.controller.id]
  iam_instance_profile = module.iam.controller_profile_name
  http_hops            = 2
  root_volume_size     = 20
  tags = {
    Name                                        = "kube-controller"
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"

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
    Name                                        = "kube-worker-${each.value}"
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
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
