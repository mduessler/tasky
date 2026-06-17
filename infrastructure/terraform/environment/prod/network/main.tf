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
    description     = "Kubernetes API server from workers"
    from_port       = 6443
    to_port         = 6443
    protocol        = "tcp"
    security_groups = [aws_security_group.worker[each.key].id]
  }

  egress {
    description     = "Kubelet API to workers"
    from_port       = 10250
    to_port         = 10250
    protocol        = "tcp"
    security_groups = [aws_security_group.worker[each.key].id]
  }

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
  description = "Security Group for the workers of the kubernetes"
  vpc_id      = each.value.id

  ingress {
    description     = "Kubelet API from controller"
    from_port       = 10250
    to_port         = 10250
    protocol        = "tcp"
    security_groups = [aws_security_group.controllers[each.key].id]
  }

  ingress {
    description     = "Pod-to-pod traffic between workers"
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.worker[each.key].id]
  }

  ingress {
    description = "HTTPS ingress from internet via NLB"
    from_port   = 30443
    to_port     = 30443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description     = "Pod-to-pod traffic to other workers"
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.worker[each.key].id]
  }

  egress {
    description     = "Kubernetes API server to controller"
    from_port       = 6443
    to_port         = 6443
    protocol        = "tcp"
    security_groups = [aws_security_group.controllers[each.key].id]
  }

  egress {
    description = "HTTPS for pulling container images from registries"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
