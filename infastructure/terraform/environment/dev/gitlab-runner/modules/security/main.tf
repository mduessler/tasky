resource "aws_iam_role" "gitlab_runner" {
  name = "${var.project_name}-gitlab-runner-role-${var.environment}-${var.runner_name}"

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
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

resource "aws_iam_instance_profile" "gitlab_runner" {
  name = "${var.project_name}-gitlab-runner-profile-${var.environment}-${var.runner_name}"
  role = aws_iam_role.gitlab_runner.name
}

locals {
  runner_policies = [
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
    "arn:aws:iam::aws:policy/AmazonVPCFullAccess",
    "arn:aws:iam::aws:policy/IAMFullAccess",
  ]
}

resource "aws_iam_role_policy_attachment" "runner" {
  for_each   = toset(local.runner_policies)
  role       = aws_iam_role.gitlab_runner.name
  policy_arn = each.value
}
