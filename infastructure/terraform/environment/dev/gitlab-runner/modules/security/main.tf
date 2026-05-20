resource "aws_iam_role" "gitlab_runner" {
  name = "tasky-gitlab-runner-role-${var.environment}-${var.runner_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Environment = var.environment
    Project     = "tasky"
    ManagedBy   = "terraform"
  }
}

resource "aws_iam_instance_profile" "gitlab_runner" {
  name = "tasky-gitlab-runner-profile-${var.environment}-${var.runner_name}"
  role = aws_iam_role.gitlab_runner.name
}

locals {
  runner_policies = [
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
  ]
}

resource "aws_iam_role_policy_attachment" "runner" {
  for_each   = toset(local.runner_policies)
  role       = aws_iam_role.gitlab_runner.name
  policy_arn = each.value
}
