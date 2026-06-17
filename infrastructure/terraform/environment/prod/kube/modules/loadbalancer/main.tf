resource "aws_lb" "nginx" {
  name               = "nginx-nlb"
  load_balancer_type = "network"
  subnets            = [var.public_subnet]
}

resource "aws_lb_target_group" "nginx" {
  name     = "nginx-tg"
  port     = 30443
  protocol = "TCP"
  vpc_id   = var.vpc_id
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
  target_id        = each.value
  port             = 30443
}
