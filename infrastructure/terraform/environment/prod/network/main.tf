module "vpcs" {
  for_each = toset(var.availability_zones)

  source            = "../../../modules/network"
  availability_zone = each.value
  environment       = var.environment

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
  description = "Security group for the Kubernetes controller."
  vpc_id      = each.value.id

  egress {
    description = "HTTPS for pulling container images from registries"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "worker" {
  for_each    = module.vpcs
  name        = "kube-worker-sg-${each.key}"
  description = "Security group for the Kubernetes workers."
  vpc_id      = each.value.id

  ingress {
    description = "Pod-to-pod traffic between workers"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  ingress {
    description = "HTTPS ingress from internet via NLB"
    from_port   = 30443
    to_port     = 30443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Pod-to-pod traffic to other workers"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  egress {
    description = "HTTPS for pulling container images from registries"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group_rule" "controller_to_worker_kubelet" {
  for_each                 = module.vpcs
  type                     = "egress"
  description              = "Kubelet API to workers"
  from_port                = 10250
  to_port                  = 10250
  protocol                 = "tcp"
  security_group_id        = aws_security_group.controllers[each.key].id
  source_security_group_id = aws_security_group.worker[each.key].id
}

resource "aws_security_group_rule" "worker_from_controller_kubelet" {
  for_each                 = module.vpcs
  type                     = "ingress"
  description              = "Kubelet API from controller"
  from_port                = 10250
  to_port                  = 10250
  protocol                 = "tcp"
  security_group_id        = aws_security_group.worker[each.key].id
  source_security_group_id = aws_security_group.controllers[each.key].id
}
