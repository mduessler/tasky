resource "aws_security_group" "nlb" {
  name        = "kube-controller-nlb-sg-${var.availability_zone}"
  description = "Security group for the controller internal NLB."
  vpc_id      = var.vpc_id

  ingress {
    description     = "Kubernetes API server from workers"
    from_port       = 6443
    to_port         = 6443
    protocol        = "tcp"
    security_groups = [var.worker_sg_id]
  }

  egress {
    description     = "Kubernetes API server to controller"
    from_port       = 6443
    to_port         = 6443
    protocol        = "tcp"
    security_groups = [var.controller_sg_id]
  }
}

resource "aws_security_group_rule" "worker_to_nlb" {
  description              = "Kubernetes API server to internal NLB"
  type                     = "egress"
  from_port                = 6443
  to_port                  = 6443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.nlb.id
  security_group_id        = var.worker_sg_id
}

resource "aws_security_group_rule" "controller_from_nlb" {
  description              = "Kubernetes API server from internal NLB"
  type                     = "ingress"
  from_port                = 6443
  to_port                  = 6443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.nlb.id
  security_group_id        = var.controller_sg_id
}

resource "aws_lb" "this" {
  name               = "kube-ctrl-nlb-${var.availability_zone}"
  load_balancer_type = "network"
  internal           = true
  subnets            = [var.subnet_id]
  security_groups    = [aws_security_group.nlb.id]
}

resource "aws_lb_target_group" "this" {
  name     = "kube-controller-tg-${var.availability_zone}"
  port     = 6443
  protocol = "TCP"
  vpc_id   = var.vpc_id
}

resource "aws_lb_listener" "this" {
  load_balancer_arn = aws_lb.this.arn
  port              = 6443
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

resource "aws_launch_template" "this" {
  name_prefix   = "kube-controller-${var.availability_zone}-"
  image_id      = var.image_id
  instance_type = var.instance_type

  iam_instance_profile {
    name = var.controller_profile_name
  }

  network_interfaces {
    subnet_id       = var.subnet_id
    security_groups = [var.controller_sg_id]
  }

  metadata_options {
    http_tokens                 = "required"
    http_endpoint               = "enabled"
    http_put_response_hop_limit = 2
  }

  block_device_mappings {
    device_name = "/dev/sda1"
    ebs {
      encrypted   = true
      volume_type = "gp3"
      volume_size = 20
    }
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name                                       = "kube-controller"
      "kubernetes.io/cluster/${var.clustername}" = "owned"
    }
  }
}

resource "aws_autoscaling_group" "this" {
  name                = "kube-controller-asg-${var.availability_zone}"
  min_size            = 1
  max_size            = 1
  desired_capacity    = 1
  vpc_zone_identifier = [var.subnet_id]
  target_group_arns   = [aws_lb_target_group.this.arn]

  launch_template {
    id      = aws_launch_template.this.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "kube-controller"
    propagate_at_launch = true
  }

  tag {
    key                 = "kubernetes.io/cluster/${var.clustername}"
    value               = "owned"
    propagate_at_launch = true
  }
}
