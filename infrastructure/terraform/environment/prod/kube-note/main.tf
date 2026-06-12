module "network" {
  source     = "../../../modules/network"
  aws_region = var.aws_region
}

resource "aws_security_group" "controller" {
  name        = "kube-controller-sg"
  description = "Security Group for the controller of the kubernetes"
  vpc_id      = module.network.vpc.id

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
  vpc_id      = module.network.vpc_id

  ingress {
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    cidr_blocks = [module.network.vpc_cidr]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

module "controller" {
  source             = "../../../modules/compute"
  ami_owners         = ["self"]
  ami_filter_values  = ["kube-node-*"]
  instance_type      = var.instance_type
  subnet_id          = module.network.private_subnet_id
  security_groups    = [aws_security_group.controller]
  iam_instance_profile = module.security.instance_profile_name
  http_hops          = 2
  root_volume_size   = 20
  namespace          = var.environment
  name               = "kube-controller"
}

module "worker" {
  for_each = var.workers

  source             = "../../../modules/compute"
  ami_owners         = ["self"]
  ami_filter_values  = ["kube-node-*"]
  instance_type      = var.instance_type
  subnet_id          = module.network.private_subnet_id
  security_groups    = [aws_security_group.worker]
  iam_instance_profile = module.security.instance_profile_name
  http_hops          = 2
  root_volume_size   = 50
  namespace          = var.environment
  name               = each.value
}
