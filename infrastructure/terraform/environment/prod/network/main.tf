module "vpcs" {
  for_each = toset(var.availability_zones)

  source            = "../../../modules/network"
  availability_zone = each.value

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.clustername}" = "owned"
    "kubernetes.io/role/internal-elb"          = "1"
  }
  public_subnet_tags = {
    "kubernetes.io/cluster/${var.clustername}" = "owned"
    "kubernetes.io/role/elb"                   = "1"
  }
}

resource "aws_security_group" "controllers" {
  for_each    = module.vpcs
  name        = "kube-controller-sg-${each.key}"
  description = "Security Group for the controller of the kubernetes"
  vpc_id      = each.value.id

  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = [each.value.vpc_cidr]
  }
  ingress {
    from_port   = 2379
    to_port     = 2380
    protocol    = "tcp"
    cidr_blocks = [each.value.vpc_cidr]
  }
  ingress {
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    cidr_blocks = [each.value.vpc_cidr]
  }
  ingress {
    from_port   = 10257
    to_port     = 10257
    protocol    = "tcp"
    cidr_blocks = [each.value.vpc_cidr]
  }
  ingress {
    from_port   = 10259
    to_port     = 10259
    protocol    = "tcp"
    cidr_blocks = [each.value.vpc_cidr]
  }
  egress { # In a real secure environment, define the outgoing connections better.
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "worker" {
  for_each    = module.vpcs
  name        = "kube-worker-sg-${each.key}"
  description = "Security Group for the workers of the kubernetes"
  vpc_id      = each.value.id

  ingress {
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    cidr_blocks = [each.value.vpc_cidr]
  }
  ingress {
    from_port   = 30443
    to_port     = 30443
    protocol    = "tcp"
    cidr_blocks = [each.value.vpc_cidr]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
